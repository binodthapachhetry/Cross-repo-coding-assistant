from aider.cross_repo_graph import CrossRepoGraph
from aider.repomap import RepoMap

class CrossRepoManager:
    def __init__(self, repos):                                                                                                           
      self.repo_maps = {repo: RepoMap(repo) for repo in repos}                                                                         
      self.cross_graph = CrossRepoGraph()  # Relationship tracking

class CrossRepoContext:                                                                                                                     
     def __init__(self, repos: List[RepoMap]):                                                                                               
         self.repo_maps = {repo.root: repo for repo in repos}                                                                                                                                                                                                
         self.global_graph = self._build_unified_graph()  # Not just appending subgraphs                                                     
                                                                                                                                             
     def _build_unified_graph(self):                                                                                                         
         # Should merge nodes with repo prefixes                                                                                             
         for repo in self.repo_maps.values():                                                                                                
             for node in repo.graph.nodes:                                                                                                   
                 self.global_graph.add_node(f"{repo.root}|{node}")  

def get_context_budget(self):                                                                                                               
     return {                                                                                                                                
         'primary': self.max_tokens * 0.6,                                                                                                   
         'secondary': self.max_tokens * 0.3,                                                                                                 
         'cross_links': self.max_tokens * 0.1                                                                                                
     } 