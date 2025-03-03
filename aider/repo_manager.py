import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set

from aider.repo import GitRepo
from aider.repomap import RepoMap
from aider.cross_repo_graph import CrossRepoGraph
from aider.io import InputOutput

class RepositoryManager:
    """
    Manages multiple Git repositories for cross-repository operations
    """
    
    def __init__(self, io: InputOutput):
        """
        Initialize the repository manager
        
        Args:
            io: InputOutput instance for user interaction
        """
        self.io = io
        self.repositories: Dict[str, GitRepo] = {}
        self.repo_maps: Dict[str, RepoMap] = {}
        self.active_repo: Optional[str] = None
        self.cross_repo_graph = CrossRepoGraph()
        
    def add_repository(self, name: str, path: str, models=None) -> GitRepo:
        """
        Add a new repository to the manager
        
        Args:
            name: Name to identify the repository
            path: Path to the repository
            models: Models to use for commit messages
            
        Returns:
            The added GitRepo instance
        """
        # Normalize path
        abs_path = os.path.abspath(path)
        
        # Check if repository already exists
        if name in self.repositories:
            self.io.tool_warning(f"Repository '{name}' already exists. Use a different name.")
            return self.repositories[name]
            
        # Check if path is already registered under a different name
        for repo_name, repo in self.repositories.items():
            if abs_path == repo.root:
                self.io.tool_warning(
                    f"Repository at {abs_path} is already registered as '{repo_name}'"
                )
                return repo
        
        try:
            # Create GitRepo instance
            repo = GitRepo(
                self.io,
                [],  # Empty file list initially
                abs_path,
                models=models,
            )
            
            # Create RepoMap instance
            repo_map = RepoMap(
                map_tokens=1024,
                root=abs_path,
                main_model=models[0] if models else None,
                io=self.io,
                name=name
            )
            
            # Store in dictionaries
            self.repositories[name] = repo
            self.repo_maps[name] = repo_map
            
            # Set as active if it's the first one
            if not self.active_repo:
                self.active_repo = name
                
            self.io.tool_output(f"Added repository '{name}' at {abs_path}")
            return repo
            
        except FileNotFoundError:
            self.io.tool_error(f"Could not find a valid git repository at {abs_path}")
            return None
        except Exception as e:
            self.io.tool_error(f"Error adding repository: {str(e)}")
            return None
    
    def get_repository(self, name: str) -> Optional[GitRepo]:
        """
        Get a repository by name
        
        Args:
            name: Name of the repository
            
        Returns:
            GitRepo instance or None if not found
        """
        if name not in self.repositories:
            self.io.tool_warning(f"Repository '{name}' not found")
            return None
        return self.repositories[name]
    
    def get_repo_map(self, name: str) -> Optional[RepoMap]:
        """
        Get a repository map by name
        
        Args:
            name: Name of the repository
            
        Returns:
            RepoMap instance or None if not found
        """
        if name not in self.repo_maps:
            self.io.tool_warning(f"Repository map for '{name}' not found")
            return None
        return self.repo_maps[name]
    
    def set_active_repository(self, name: str) -> bool:
        """
        Set the active repository
        
        Args:
            name: Name of the repository to set as active
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.repositories:
            self.io.tool_warning(f"Repository '{name}' not found")
            return False
        
        self.active_repo = name
        self.io.tool_output(f"Active repository set to '{name}'")
        return True
    
    def get_active_repository(self) -> Optional[GitRepo]:
        """
        Get the currently active repository
        
        Returns:
            Active GitRepo instance or None if no active repository
        """
        if not self.active_repo:
            self.io.tool_warning("No active repository set")
            return None
        return self.repositories[self.active_repo]
    
    def get_active_repo_map(self) -> Optional[RepoMap]:
        """
        Get the currently active repository map
        
        Returns:
            Active RepoMap instance or None if no active repository
        """
        if not self.active_repo:
            return None
        return self.repo_maps[self.active_repo]
    
    def list_repositories(self) -> List[Tuple[str, str, bool]]:
        """
        List all repositories
        
        Returns:
            List of tuples (name, path, is_active)
        """
        return [
            (name, repo.root, name == self.active_repo)
            for name, repo in self.repositories.items()
        ]
    
    def resolve_path(self, repo_prefixed_path: str) -> Tuple[Optional[GitRepo], str]:
        """
        Resolve a repo-prefixed path to a (repo, relative_path) tuple
        
        Args:
            repo_prefixed_path: Path with optional repo prefix (e.g., "repo1/path/to/file.py")
            
        Returns:
            Tuple of (GitRepo, relative_path) or (None, original_path) if no prefix
        """
        if "/" not in repo_prefixed_path:
            # No prefix, use active repository
            if not self.active_repo:
                self.io.tool_warning("No active repository set")
                return None, repo_prefixed_path
            return self.repositories[self.active_repo], repo_prefixed_path
        
        # Split on first slash
        repo_name, rel_path = repo_prefixed_path.split("/", 1)
        
        if repo_name in self.repositories:
            return self.repositories[repo_name], rel_path
        
        # If no matching repository, assume it's a path in the active repository
        if not self.active_repo:
            self.io.tool_warning("No active repository set")
            return None, repo_prefixed_path
            
        return self.repositories[self.active_repo], repo_prefixed_path
    
    def build_cross_repo_graph(self):
        """
        Build the cross-repository graph from all repositories
        """
        for name, repo_map in self.repo_maps.items():
            # Ensure each repo has built its dependency graph
            repo_map.build_dependency_graph()
            
            # Add to cross-repo graph
            self.cross_repo_graph.add_repo(name, repo_map.G)
        
        self.io.tool_output("Built cross-repository dependency graph")
    
    def find_integration_points(self) -> List[dict]:
        """
        Find potential integration points between repositories
        
        Returns:
            List of dictionaries describing integration points
        """
        # Ensure graph is built
        if not self.cross_repo_graph.graph.edges():
            self.build_cross_repo_graph()
            
        return self.cross_repo_graph.find_integration_points()
    
    def get_all_files(self) -> Dict[str, List[str]]:
        """
        Get all files from all repositories
        
        Returns:
            Dictionary mapping repository names to lists of files
        """
        result = {}
        for name, repo in self.repositories.items():
            result[name] = repo.get_tracked_files()
        return result
    
    def get_all_repo_maps(self) -> List[RepoMap]:
        """
        Get all repository maps
        
        Returns:
            List of RepoMap instances
        """
        return list(self.repo_maps.values())
