from collections import defaultdict
import networkx as nx

class IntegrationAnalyzer:
    def __init__(self, repos: list):                                                                                                              
        self.repos = repos  # Store list of RepoMap instances 
        self.global_graph = self._build_global_dependency_graph()
        self.endpoints = self._collect_api_endpoints()                                                                                      
        self.consumers = self._collect_api_consumers() 

    def _build_global_dependency_graph(self):                                                                                               
        # Create a networkx graph combining dependencies from all repos                                                                     
        graph = nx.DiGraph()

        # First add all nodes from both repos                                                                                                   
        for repo in self.repos:  
            repo.build_dependency_graph()

            # Add nodes from this repo's graph                                                                                              
            for node in repo.G.nodes():                                                                                                     
                graph.add_node(node, repo=repo.root)                                                                                        
                                                                                                                                             
             # Add edges from this repo's graph                                                                                              
            graph.add_edges_from(repo.G.edges(data=True)) 

        return graph  
    
    def match_endpoints(self):                                                                                                    
         # Find API consumer/provider pairs across repos                                                                                     
        matches = []     

        print("\n[Debug] API Endpoints:")                                                                                                   
        for path, tags in self.endpoints.items():                                                                                           
            print(f"  {path} from:")                                                                                                        
            for tag in tags:                                                                                                                
                print(f"    - {tag.rel_fname}:{tag.line}")                                                                                  
                                                                                                                                            
        print("\n[Debug] API Consumers:")                                                                                                   
        for consumer_path, tag in self.consumers:                                                                                           
            print(f"  {consumer_path} from:")                                                                                               
            print(f"    - {tag.rel_fname}:{tag.line}") 

        for consumer_path, consumer_tag in self.consumers:                                                                                   
            # Look for exact matches first                                                                                                      
            if consumer_path in self.endpoints:                                                                                                 
                matches.extend(                                                                                                                 
                    (consumer_tag, endpoint_tag)                                                                                                
                    for endpoint_tag in self.endpoints[consumer_path]                                                                           
                ) 

        return matches 

    def find_transitive_deps(self, entity):                                                                                                     
        # ✅ Should track across repo boundaries                                                                                                
        return [                                                                                                                                
            f"{dep_repo}|{dep}"                                                                                                                 
            for dep in nx.descendants(self.global_graph, entity)                                                                                
            if "|" in dep  # Cross-repo dependency                                                                                              
        ]

    def find_consumers(self):                                                                                                               
        """Identify API consumers in frontend repos"""                                                                                      
        return [                                                                                                                            
            node for node in self.global_graph.nodes                                                                                        
            if "src/components/" in node  # Example pattern match                                                                           
            and ":handle" in node  # Example handler convention                                                                             
        ]  
         
    def _normalize_path(self, path):                                                                                                        
        """Normalize API paths for comparison"""                                                                                            
        # path = path.strip("'\"")  # Remove quotes                                                                                           
        # path = path.lower()                                                                                                                 
        # path = path.rstrip('/')                                                                                                             
        # # Remove common API prefixes                                                                                                            
        # # Test-specific normalization                                                                                                           
        # if path.startswith('/auth'):                                                                                                            
        #     return path[1:]  # 'auth/login' instead of '/auth/login'  
                                                                           
        path = path.strip("'\"")  # Remove quotes                                                                                               
        path = path.lower().rstrip('/')                                                                                                         
        return path.split('?')[0]   

    def _collect_api_endpoints(self):                                                                                                       
         endpoints = defaultdict(list)                                                                                                       
         for repo in self.repos:                                                                                                             
             for tag in repo.get_all_tags():                                                                                                     
                 if tag.kind == "api_route":                                                                                                 
                     norm_path = self._normalize_path(tag.name)                                                                              
                     endpoints[norm_path].append(tag)                                                                                        
         return endpoints                                                                                                                    
                                                                                                                                             
    def _collect_api_consumers(self):                                                                                                       
        consumers = []                                                                                                                      
        for repo in self.repos:                                                                                                             
            for tag in repo.get_all_tags():                                                                                                     
                if tag.kind == "api_consumer":                                                                                              
                    norm_path = self._normalize_path(tag.name)                                                                              
                    consumers.append((norm_path, tag))                                                                                      
        return consumers                                                                                                                              
                                                                                                                                             
    def find_providers(self):                                                                                                               
        """Identify API providers in backend repos"""                                                                                       
        return [                                                                                                                            
            node for node in self.global_graph.nodes                                                                                        
            if "api/" in node  # Example API route pattern                                                                                  
            and ".py:" in node  # Python endpoint definitions                                                                               
        ]                                                                                                                                   
                                                                                                                                            
    def _parameters_match(self, consumer_params, provider_params):                                                                          
        """Simple parameter type matching (implementation stub)"""                                                                          
        # For test purposes, assume basic match when param counts align                                                                     
        return len(consumer_params) == len(provider_params)   

    def print_debug_info(self):                                                                                                                 
        print("\n=== API Endpoints ===")                                                                                                        
        for path, tags in self.endpoints.items():                                                                                               
            print(f"Path: {path}")                                                                                                              
            for tag in tags:                                                                                                                    
                print(f"  - {tag.rel_fname}:{tag.line}")                                                                                        
                                                                                                                                                
        print("\n=== API Consumers ===")                                                                                                        
        for path, tag in self.consumers:                                                                                                        
            print(f"Path: {path}")                                                                                                              
            print(f"  - {tag.rel_fname}:{tag.line}")                                                                                                                                                                                                                  
        