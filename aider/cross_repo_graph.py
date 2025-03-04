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
import itertools
import networkx as nx
from typing import Dict, List, Set, Tuple, Optional

class CrossRepoGraph:
    """
    Manages a graph of relationships between multiple repositories
    """
    
    def __init__(self):
        """Initialize the cross-repository graph"""
        self.graph = nx.MultiDiGraph()
        self.repos = {}
        
    def add_repo(self, repo_name: str, repo_graph: nx.MultiDiGraph):
        """
        Add a repository's dependency graph to the cross-repository graph
        
        Args:
            repo_name: Name of the repository
            repo_graph: NetworkX graph of the repository's dependencies
        """
        self.repos[repo_name] = repo_graph
        
        # Add nodes with repository attribute
        for node in repo_graph.nodes():
            node_id = f"{repo_name}:{node}"
            node_data = repo_graph.nodes[node].copy() if repo_graph.nodes[node] else {}
            node_data['repo'] = repo_name
            node_data['name'] = node
            self.graph.add_node(node_id, **node_data)
        
        # Add edges with repository attribute
        for src, dst, key, data in repo_graph.edges(data=True, keys=True):
            src_id = f"{repo_name}:{src}"
            dst_id = f"{repo_name}:{dst}"
            edge_data = data.copy()
            edge_data['repo'] = repo_name
            self.graph.add_edge(src_id, dst_id, key=key, **edge_data)
    
    def update_nodes(self, repo_name: str, nodes: List[str]):
        """
        Update specific nodes from a repository
        
        Args:
            repo_name: Name of the repository
            nodes: List of node names to update
        """
        if repo_name not in self.repos:
            return
            
        repo_graph = self.repos[repo_name]
        
        # Remove existing nodes
        for node in nodes:
            node_id = f"{repo_name}:{node}"
            if node_id in self.graph:
                self.graph.remove_node(node_id)
        
        # Add updated nodes
        for node in nodes:
            if node in repo_graph:
                node_id = f"{repo_name}:{node}"
                node_data = repo_graph.nodes[node].copy() if repo_graph.nodes[node] else {}
                node_data['repo'] = repo_name
                node_data['name'] = node
                self.graph.add_node(node_id, **node_data)
                
                # Add edges
                for src, dst, key, data in repo_graph.out_edges(node, data=True, keys=True):
                    if dst in nodes:  # Only add edges to other updated nodes
                        src_id = f"{repo_name}:{src}"
                        dst_id = f"{repo_name}:{dst}"
                        edge_data = data.copy()
                        edge_data['repo'] = repo_name
                        self.graph.add_edge(src_id, dst_id, key=key, **edge_data)
    
    def find_integration_points(self) -> List[Dict]:
        """
        Find potential integration points between repositories
        
        Returns:
            List of dictionaries describing integration points
        """
        integration_points = []
        
        # For each pair of repositories
        for repo1, repo2 in itertools.combinations(self.repos.keys(), 2):
            repo1_nodes = [n for n, d in self.graph.nodes(data=True) if d.get('repo') == repo1]
            repo2_nodes = [n for n, d in self.graph.nodes(data=True) if d.get('repo') == repo2]
            
            # Find shared symbols (same name in both repos)
            shared_symbols = self._find_shared_symbols(repo1, repo2, repo1_nodes, repo2_nodes)
            
            # Find potential API connections
            api_connections = self._find_api_connections(repo1, repo2, repo1_nodes, repo2_nodes)
            
            if shared_symbols or api_connections:
                integration_points.append({
                    'repos': (repo1, repo2),
                    'shared_symbols': shared_symbols,
                    'api_connections': api_connections
                })
        
        return integration_points
    
    def _find_shared_symbols(self, repo1: str, repo2: str, 
                            repo1_nodes: List[str], repo2_nodes: List[str]) -> List[Dict]:
        """
        Find symbols with the same name in both repositories
        
        Args:
            repo1: First repository name
            repo2: Second repository name
            repo1_nodes: Nodes from first repository
            repo2_nodes: Nodes from second repository
            
        Returns:
            List of shared symbols with metadata
        """
        shared_symbols = []
        
        # Extract base names (without repo prefix)
        repo1_names = {n.split(':', 1)[1] for n in repo1_nodes}
        repo2_names = {n.split(':', 1)[1] for n in repo2_nodes}
        
        # Find intersection
        common_names = repo1_names.intersection(repo2_names)
        
        for name in common_names:
            repo1_node = f"{repo1}:{name}"
            repo2_node = f"{repo2}:{name}"
            
            # Get node metadata
            repo1_data = self.graph.nodes[repo1_node]
            repo2_data = self.graph.nodes[repo2_node]
            
            # Check if they're the same type of symbol
            if repo1_data.get('type') == repo2_data.get('type'):
                shared_symbols.append({
                    'name': name,
                    'type': repo1_data.get('type', 'unknown'),
                    'repo1_file': repo1_data.get('file'),
                    'repo2_file': repo2_data.get('file')
                })
        
        return shared_symbols
    
    def _find_api_connections(self, repo1: str, repo2: str,
                             repo1_nodes: List[str], repo2_nodes: List[str]) -> List[Dict]:
        """
        Find potential API connections between repositories
        
        Args:
            repo1: First repository name
            repo2: Second repository name
            repo1_nodes: Nodes from first repository
            repo2_nodes: Nodes from second repository
            
        Returns:
            List of potential API connections
        """
        api_connections = []
        
        # Look for nodes that could be APIs (classes, functions, etc.)
        api_types = {'class', 'function', 'method', 'module'}
        
        repo1_apis = [n for n in repo1_nodes 
                     if self.graph.nodes[n].get('type') in api_types]
        repo2_apis = [n for n in repo2_nodes 
                     if self.graph.nodes[n].get('type') in api_types]
        
        # For each API in repo1, find similar APIs in repo2
        for api1 in repo1_apis:
            api1_name = api1.split(':', 1)[1]
            
            for api2 in repo2_apis:
                api2_name = api2.split(':', 1)[1]
                
                # Check for name similarity
                if (api1_name.lower() in api2_name.lower() or 
                    api2_name.lower() in api1_name.lower()):
                    
                    # Get node metadata
                    api1_data = self.graph.nodes[api1]
                    api2_data = self.graph.nodes[api2]
                    
                    api_connections.append({
                        'repo1_api': api1_name,
                        'repo2_api': api2_name,
                        'type': api1_data.get('type', 'unknown'),
                        'repo1_file': api1_data.get('file'),
                        'repo2_file': api2_data.get('file'),
                        'similarity': 'name_substring'
                    })
        
        return api_connections
    
    def get_cross_repo_dependencies(self) -> Dict[str, Set[str]]:
        """
        Get dependencies between repositories
        
        Returns:
            Dictionary mapping repository names to sets of dependent repositories
        """
        dependencies = {repo: set() for repo in self.repos}
        
        # Check for potential dependencies based on shared symbols
        integration_points = self.find_integration_points()
        
        for point in integration_points:
            repo1, repo2 = point['repos']
            
            # If there are shared symbols or API connections, consider them potentially dependent
            if point['shared_symbols'] or point['api_connections']:
                dependencies[repo1].add(repo2)
                dependencies[repo2].add(repo1)
        
        return dependencies
    
    def visualize(self, output_file: str = "cross_repo_graph.png"):
        """
        Visualize the cross-repository graph
        
        Args:
            output_file: Path to save the visualization
        """
        try:
            import matplotlib.pyplot as plt
            
            # Create a simplified graph for visualization
            vis_graph = nx.DiGraph()
            
            # Add nodes with repository as color
            for node, data in self.graph.nodes(data=True):
                repo = data.get('repo', 'unknown')
                vis_graph.add_node(node, repo=repo)
            
            # Add edges
            for src, dst in self.graph.edges():
                vis_graph.add_edge(src, dst)
            
            # Set up colors by repository
            repos = list(self.repos.keys())
            colors = plt.cm.tab10(range(len(repos)))
            color_map = {repo: colors[i] for i, repo in enumerate(repos)}
            
            # Get node colors
            node_colors = [color_map[self.graph.nodes[n]['repo']] for n in vis_graph.nodes()]
            
            # Create the plot
            plt.figure(figsize=(12, 10))
            pos = nx.spring_layout(vis_graph, seed=42)
            nx.draw_networkx(
                vis_graph, 
                pos=pos,
                node_color=node_colors,
                node_size=50,
                with_labels=False,
                arrows=True,
                alpha=0.7
            )
            
            # Add legend
            for i, repo in enumerate(repos):
                plt.scatter([], [], color=colors[i], label=repo)
            plt.legend()
            
            plt.title("Cross-Repository Dependency Graph")
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(output_file, dpi=300)
            plt.close()
            
            return True
        except ImportError:
            return False
