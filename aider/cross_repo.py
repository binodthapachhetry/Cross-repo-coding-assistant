from aider.cross_repo_graph import CrossRepoGraph
from aider.repomap import RepoMap

class CrossRepoManager:
    def __init__(self, repos):                                                                                                           
      self.repo_maps = {repo: RepoMap(repo) for repo in repos}                                                                         
      self.cross_graph = CrossRepoGraph()  # Relationship tracking

class CrossRepoContext:                                                                                                                     
    def __init__(self, repos: List[RepoMap]):                                                                                               
        self.graph = self.build_global_graph(repos)                                                                                         
                                                                                                                                            
    def build_global_graph(self):                                                                                                           
        # Combine individual repo graphs into unified structure                                                                             
        global_graph = nx.DiGraph()                                                                                                         
        for repo in repos:                                                                                                                  
            global_graph = nx.compose(global_graph, repo.graph)                                                                             
        return global_graph 