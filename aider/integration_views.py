class IntegrationSpotlight:                                                                                                              
    def show_entity_connections(self, entity):                                                                                           
        # Visualize cross-repo relationships                                                                                             
        self.render_graph(self.cross_graph.get_connections(entity)) 