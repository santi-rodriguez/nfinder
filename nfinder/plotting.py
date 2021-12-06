import matplotlib.pyplot as plt
import napari

def plot_layout(points, node_size=5, img=None, cmap='gray', color='white', ax=None, viewer=None, scale=None):
    """Plot positions of nodes. If 'img' is not None, this function shows the overlap between the positions of nodes and the given image."""
    if points.shape[1]<=2:
        if ax is None:
            figsize = (6, 6)
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.figure

        if img is not None:
            ax.imshow(img, cmap=cmap)

        ax.plot(points[:, 1], points[:, 0], 'o', markersize=node_size, color=color)     
        return ax

    else:
        if viewer is None:
            viewer = napari.Viewer(ndisplay=3)
        if img is not None:
            rendering = 'additive'
            viewer.add_image(img[:, :, :, 1], gamma=0.35, colormap='green', rendering=rendering, scale=scale, name='membrane')
            viewer.add_image(img[:, :, :, 0], gamma=0.25, opacity=0.7, colormap='red', rendering=rendering, scale=scale, name='nuclei')
        viewer.add_points(points, size=node_size/2, opacity=0.3, edge_color=color, face_color=color, scale=scale, name='centroids')
        
        return viewer
    
    

def plot_neighbors_graph(points, edges, color='white', scale=None, ax=None, **kwargs):
    """Plot the neighbors graph given by set points and edge positions."""
    #If edges contains node indexes, convert them to spatial positions
    ndim = edges.ndim
    if  ndim == 2:
        edges = points[edges]
    
    if points.shape[1]<=2:
        if ax is None:
            figsize = (6, 6)
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.figure        

        for source, target in edges:
            ax.plot([source[1], target[1]], [source[0], target[0]], ls='-', color=color)

        plot_layout(points, color=color, ax=ax, **kwargs)

        ax.set_facecolor('black')
        ax.set(xticks=[], yticks=[])
        return ax
    
    else:
        viewer = plot_layout(points, color=color, scale=scale, **kwargs)
        viewer.add_shapes(edges, shape_type='line', opacity=0.3, edge_width=0.5, edge_color=color, name='edges', scale=scale)
        return viewer


def plot_overlap(img, points, edges, show_titles=False, axes=None, **kwargs):
    if points.shape[1]<=2:
        if axes is None:
            figsize = (10, 5)
            fig, axes = plt.subplots(1, 2, figsize=figsize)
            #Adjust spacing between axes
            fig.tight_layout(pad=0)
            fig.subplots_adjust(wspace=0.05)
        else:
            fig = axes[0].figure

        axes[0].imshow(img)
        plot_neighbors_graph(points, edges, img=img, ax=axes[1], **kwargs)

        for ax in axes:
            ax.axis('off')

        if show_titles:
            titles = ['Sample', 'Neighbors graph']
            titlesize = 18
            for t, ax in zip(titles, axes):
                ax.set_title(t, size=titlesize)

        return axes
    
    else:
        plot_neighbors_graph(points, edges, img=img, **kwargs)
        