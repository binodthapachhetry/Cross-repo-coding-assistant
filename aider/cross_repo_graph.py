import networkx as nx
import logging
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)

class CrossRepoGraph:
    """
    Manages a graph of relationships between multiple repositories
    """
    
    def __init__(self):
        """Initialize the cross-repository graph"""
        self.graph = nx.MultiDiGraph()
        self.repo_nodes = {}  # Maps repo name to set of nodes
        
    def add_repo(self, repo_name: str, repo_graph: nx.MultiDiGraph):
        """
        Add a repository's graph to the cross-repository graph
        
        Args:
            repo_name: Name of the repository
            repo_graph: The repository's dependency graph
        """
        # Track nodes for this repo
        self.repo_nodes[repo_name] = set()
        
        # Add nodes with repo prefix
        for node, attrs in repo_graph.nodes(data=True):
            prefixed_node = f"{repo_name}:{node}"
            self.graph.add_node(prefixed_node, **attrs, repo=repo_name)
            self.repo_nodes[repo_name].add(prefixed_node)
            
        # Add edges with repo prefix
        for src, dst, key, data in repo_graph.edges(data=True, keys=True):
            self.graph.add_edge(
                f"{repo_name}:{src}", 
                f"{repo_name}:{dst}", 
                key=key,
                **data
            )
    
    def find_integration_points(self) -> List[Dict]:
        """
        Find potential integration points between repositories
        
        Returns:
            List of dictionaries describing integration points
        """
        integration_points = []
        
        # Find nodes with similar names across repos
        node_name_map = {}
        for repo, nodes in self.repo_nodes.items():
            for node in nodes:
                # Extract base name without repo prefix
                base_name = node.split(':', 1)[1]
                if base_name not in node_name_map:
                    node_name_map[base_name] = []
                node_name_map[base_name].append((repo, node))
        
        # Find nodes that appear in multiple repos
        for base_name, occurrences in node_name_map.items():
            if len(occurrences) > 1:
                repos = [repo for repo, _ in occurrences]
                integration_points.append({
                    "type": "shared_node",
                    "name": base_name,
                    "repos": repos
                })
        
        # Find API endpoints and consumers
        api_endpoints = {}
        api_consumers = {}
        
        for repo, nodes in self.repo_nodes.items():
            for node in nodes:
                attrs = self.graph.nodes[node]
                if attrs.get('type') == 'api_route':
                    route = attrs.get('route')
                    if route:
                        if route not in api_endpoints:
                            api_endpoints[route] = []
                        api_endpoints[route].append((repo, node))
                
                if attrs.get('type') == 'api_consumer':
                    url = attrs.get('url')
                    if url:
                        if url not in api_consumers:
                            api_consumers[url] = []
                        api_consumers[url].append((repo, node))
        
        # Match API endpoints with consumers
        for route, endpoints in api_endpoints.items():
            for url, consumers in api_consumers.items():
                if route in url:  # Simple matching, could be improved
                    endpoint_repos = [repo for repo, _ in endpoints]
                    consumer_repos = [repo for repo, _ in consumers]
                    
                    # Only add if they're in different repos
                    if set(endpoint_repos) != set(consumer_repos):
                        integration_points.append({
                            "type": "api_connection",
                            "route": route,
                            "provider_repos": endpoint_repos,
                            "consumer_repos": consumer_repos
                        })
        
        return integration_points
    
    def get_cross_repo_connections(self) -> List[Tuple[str, str, Dict]]:
        """
        Get all connections between different repositories
        
        Returns:
            List of tuples (repo1, repo2, connection_data)
        """
        connections = []
        
        # Check each pair of repositories
        repos = list(self.repo_nodes.keys())
        for i in range(len(repos)):
            for j in range(i+1, len(repos)):
                repo1 = repos[i]
                repo2 = repos[j]
                
                # Find connections between these repos
                repo1_nodes = self.repo_nodes[repo1]
                repo2_nodes = self.repo_nodes[repo2]
                
                # Check for shared symbols
                shared_symbols = self._find_shared_symbols(repo1, repo2, repo1_nodes, repo2_nodes)
                if shared_symbols:
                    connections.append((repo1, repo2, {
                        "type": "shared_symbols",
                        "symbols": shared_symbols
                    }))
                
                # Check for API connections
                api_connections = self._find_api_connections(repo1, repo2, repo1_nodes, repo2_nodes)
                if api_connections:
                    connections.append((repo1, repo2, {
                        "type": "api_connections",
                        "connections": api_connections
                    }))
        
        return connections
    
    def _find_shared_symbols(self, repo1, repo2, repo1_nodes, repo2_nodes) -> List[str]:
        """Find symbols that are shared between two repositories"""
        repo1_symbols = set()
        repo2_symbols = set()
        
        for node in repo1_nodes:
            attrs = self.graph.nodes[node]
            if attrs.get('kind') in ('def', 'ref'):
                repo1_symbols.add(attrs.get('name'))
        
        for node in repo2_nodes:
            attrs = self.graph.nodes[node]
            if attrs.get('kind') in ('def', 'ref'):
                repo2_symbols.add(attrs.get('name'))
        
        return list(repo1_symbols.intersection(repo2_symbols))
    
    def _find_api_connections(self, repo1, repo2, repo1_nodes, repo2_nodes) -> List[Dict]:
        """Find API connections between two repositories"""
        connections = []
        
        # Find API routes in repo1
        repo1_routes = {}
        for node in repo1_nodes:
            attrs = self.graph.nodes[node]
            if attrs.get('type') == 'api_route':
                route = attrs.get('route')
                if route:
                    repo1_routes[route] = node
        
        # Find API consumers in repo2 that match routes in repo1
        for node in repo2_nodes:
            attrs = self.graph.nodes[node]
            if attrs.get('type') == 'api_consumer':
                url = attrs.get('url')
                if url:
                    for route, route_node in repo1_routes.items():
                        if route in url:
                            connections.append({
                                "provider": {"repo": repo1, "node": route_node, "route": route},
                                "consumer": {"repo": repo2, "node": node, "url": url}
                            })
        
        # Now check the reverse: routes in repo2, consumers in repo1
        repo2_routes = {}
        for node in repo2_nodes:
            attrs = self.graph.nodes[node]
            if attrs.get('type') == 'api_route':
                route = attrs.get('route')
                if route:
                    repo2_routes[route] = node
        
        for node in repo1_nodes:
            attrs = self.graph.nodes[node]
            if attrs.get('type') == 'api_consumer':
                url = attrs.get('url')
                if url:
                    for route, route_node in repo2_routes.items():
                        if route in url:
                            connections.append({
                                "provider": {"repo": repo2, "node": route_node, "route": route},
                                "consumer": {"repo": repo1, "node": node, "url": url}
                            })
        
        return connections
