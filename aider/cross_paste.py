class CrossRepoPaste:                                                                                                                       
    def adapt_entity(self, source_entity, target_repo):                                                                                     
        # 1. Namespace adaptation                                                                                                           
        if source_entity.repo != target_repo:                                                                                               
            entity.code = self._rewrite_namespace(entity.code)                                                                              
                                                                                                                                            
        # 2. Dependency resolution                                                                                                          
        deps = self.find_cross_dependencies(entity)                                                                                         
                                                                                                                                            
        # 3. Type alignment                                                                                                                 
        return self.align_types(entity.code, target_repo.context) 