

class IntegrationAnalyzer:                                                                                                                  
    def match_endpoints(self):                                                                                                    
         # Find API consumer/provider pairs across repos                                                                                     
        return [                                                                                                                            
            (consumer, provider)                                                                                                            
            for consumer in self.find_consumers()                                                                                           
            for provider in self.find_providers()                                                                                           
            if self._parameters_match(                                                                                                      
                consumer['params'],                                                                                                         
                provider['params']                                                                                                          
            )                                                                                                                               
        ]  

def find_transitive_deps(self, entity):                                                                                                     
     # ✅ Should track across repo boundaries                                                                                                
    return [                                                                                                                                
        f"{dep_repo}|{dep}"                                                                                                                 
        for dep in nx.descendants(self.global_graph, entity)                                                                                
        if "|" in dep  # Cross-repo dependency                                                                                              
    ]                                                                                                                                       
        