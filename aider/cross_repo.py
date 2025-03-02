import os
import networkx as nx
from typing import List, Dict, Set
from pathlib import Path
import logging

from aider.repomap import RepoMap

logger = logging.getLogger(__name__)

class CrossRepoContext:
    """Manages relationships between multiple repositories"""
    
    def __init__(self, repos: List[RepoMap]):
        """
        Initialize with multiple repository maps
        
        Args:
            repos: List of RepoMap objects representing different repositories
        """
        self.repo_maps = {repo.root: repo for repo in repos}
        self.global_graph = self._build_unified_graph()
        self.max_tokens = 0  # Will be set based on model capabilities
        
    def _build_unified_graph(self):
        """
        Build a unified graph combining all repository dependency graphs
        with prefixed node names to avoid collisions
        """
        G = nx.MultiDiGraph()
        
        # First ensure all repos have built their dependency graphs
        for repo_name, repo in self.repo_maps.items():
            if not hasattr(repo, 'G') or len(repo.G.edges()) == 0:
                try:
                    repo.build_dependency_graph()
                except Exception as e:
                    logger.warning(f"Failed to build dependency graph for {repo_name}: {e}")
        
        # Now merge all graphs with prefixed nodes
        for repo_name, repo in self.repo_maps.items():
            if hasattr(repo, 'G'):
                # Add nodes with repo prefix
                for node, attrs in repo.G.nodes(data=True):
                    G.add_node(f"{repo_name}:{node}", **attrs, repo=repo_name)
                
                # Add edges with repo prefix
                for src, dst, data in repo.G.edges(data=True):
                    G.add_edge(
                        f"{repo_name}:{src}", 
                        f"{repo_name}:{dst}", 
                        **data
                    )
        
        return G
    
    def find_cross_repo_connections(self):
        """
        Find potential connections between repositories based on:
        - Similar file names
        - Similar symbol names
        - API endpoints and consumers
        
        Returns:
            List of potential connections between repositories
        """
        connections = []
        
        # Get all symbols from all repos
        repo_symbols = {}
        for repo_name, repo in self.repo_maps.items():
            symbols = set()
            for tag in repo.get_all_tags():
                if tag.kind in ("def", "ref"):
                    symbols.add(tag.name)
            repo_symbols[repo_name] = symbols
        
        # Find common symbols between repos
        repo_names = list(self.repo_maps.keys())
        for i in range(len(repo_names)):
            for j in range(i+1, len(repo_names)):
                repo1 = repo_names[i]
                repo2 = repo_names[j]
                
                common_symbols = repo_symbols[repo1].intersection(repo_symbols[repo2])
                if common_symbols:
                    connections.append({
                        "type": "shared_symbols",
                        "repo1": repo1,
                        "repo2": repo2,
                        "symbols": list(common_symbols)[:10]  # Limit to 10 examples
                    })
        
        return connections
    
    def get_context_budget(self, total_tokens):
        """
        Allocate token budget for different parts of the context
        
        Args:
            total_tokens: Total available tokens for context
            
        Returns:
            Dictionary with token allocations
        """
        self.max_tokens = total_tokens
        return {
            'primary_repo': int(total_tokens * 0.6),
            'secondary_repos': int(total_tokens * 0.3),
            'cross_links': int(total_tokens * 0.1)
        }
    
    def get_relevant_links(self):
        """
        Get a formatted string of relevant cross-repository links
        
        Returns:
            String containing relevant cross-repository relationships
        """
        connections = self.find_cross_repo_connections()
        if not connections:
            return "No cross-repository relationships detected."
        
        result = []
        for conn in connections:
            if conn["type"] == "shared_symbols":
                repo1 = os.path.basename(conn["repo1"])
                repo2 = os.path.basename(conn["repo2"])
                symbols = ", ".join(conn["symbols"][:5])
                result.append(f"- {repo1} and {repo2} share symbols: {symbols}")
        
        return "\n".join(result)
    
    def get_relations(self):
        """
        Get a comprehensive context of cross-repository relationships
        
        Returns:
            String containing detailed cross-repository context
        """
        connections = self.find_cross_repo_connections()
        if not connections:
            return ""
        
        result = ["## Cross-Repository Relationships"]
        
        for conn in connections:
            if conn["type"] == "shared_symbols":
                repo1 = os.path.basename(conn["repo1"])
                repo2 = os.path.basename(conn["repo2"])
                symbols = ", ".join(conn["symbols"])
                result.append(f"### Shared symbols between {repo1} and {repo2}")
                result.append(f"Common symbols: {symbols}")
                result.append("")
        
        return "\n".join(result)
