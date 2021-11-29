import napari
from magicgui import magicgui

def find():
    from napari.qt.threading import thread_worker
    from nfinder import get_centroids, neighbors_graph
    
    @magicgui(
        Labels={'label': 'Labels'},
        call_button='Find neighbors',
        persist=True,
    )
    def widget(
        viewer: napari.Viewer,
        Labels: napari.layers.Labels
    ) -> napari.types.ShapesData:

        def add_layer(edges):
            viewer.add_shapes(
                edges, 
                name='edges', 
                shape_type='line', 
                edge_width=0.5, 
                edge_color='white',
                scale=Labels.scale
            )

        @thread_worker
        def run(labels):
            #Find centroids
            points = get_centroids(labels)
            #Find neighbors graph
            edges = neighbors_graph(points)
            return edges

        worker = run(Labels.data)
        worker.returned.connect(add_layer)
        worker.start()
        
    return widget