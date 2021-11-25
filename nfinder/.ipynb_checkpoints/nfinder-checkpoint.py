from . import util, plotting
import numpy as np
import pandas as pd
from skimage.measure import regionprops
from skimage.io import imread
from scipy import spatial

def get(filename):
    return imread('./test_images/'+filename)
       
def data(name):
    merge_dir = 'merge_'+name+'.tif'
    labels_dir = 'segmentation_'+name+'.tif'
    return get(merge_dir), get(labels_dir)

def get_centroids(labels):
    cellprops = regionprops(labels)
    return np.round([cell.centroid for cell in cellprops]).astype(int)

def get_angle(points, simplices):
    """Compute the communicability angle of each edge"""
    A_idx, B_idx, C_idx = util.simp_permutations(simplices)
    A, B, C = points[A_idx], points[B_idx], points[C_idx]
    CA_unit = util.normalized_vector(A-C)
    CB_unit = util.normalized_vector(B-C)
    
    if len(CA_unit.shape)>1:
        return np.arccos((CA_unit*CB_unit).sum(axis=1))*180/np.pi
    
    return np.arccos((CA_unit*CB_unit).sum())*180/np.pi


def get_max(points):
    """Compute maximum communicability angle and cell-cell distance."""
    #Max distance
    #Calculate convex hull
    hull = spatial.ConvexHull(points)
    hull_points = points[hull.vertices,:]
    
    # Get the farthest apart points
    dist_max = spatial.distance.cdist(hull_points, hull_points, metric='euclidean').max()
    return np.array([180, dist_max])


def normalize(x, points):
    """Min-Max normalization"""
    x = np.array(x)
    xmax = get_max(points)
    xmin = x.min(axis=0)
    return (x-xmin)/(xmax-xmin)


def loss(x, points):
    x = normalize(x, points)
    if x.ndim==1:
        return x
    return np.mean(x, axis=1)


def ecdf(x):
    """Compute the N-dimensional Empirical Cumulative Distribution Function (ECDF) of x"""
    x = np.array(x)
    is1d = x.ndim==1
    n = len(x)
    if is1d:
        x = np.sort(x)
        F = np.arange(1, n+1) / n
    else:
        #Note: x is dominated by y if x_i <= y_i for all i.
        #Order by 1-norm to reduce search of dominated nodes
        idx = x.sum(axis=1).argsort()
        x = x[idx]
        #Count dominated nodes
        F = np.array([(x[:i+1]<=x[i]).all(axis=1).sum() for i in range(n)])/n
    return x, F


def efficiency(x, points):
    """Calculates the communicability efficiency of a set of points linked by edges which attributes are detailed in the array x"""
    x, F = ecdf(x)
    L = loss(x, points)   
    return x, np.clip(F-L, 0, 1)

    
def get_thresholds(x, points):
    x, E = efficiency(x, points)
    return x[np.where(E==E.max())[0][0]]

def edgeprops(points):
    simplices = spatial.Delaunay(points).simplices
    if simplices.shape[1]==4:
        simplices = util.reshape_simp(simplices) 
    #Edge properties
    edges_idx = util.simp2edge(simplices)
    df_edges = pd.DataFrame(edges_idx, columns=['source', 'target'])
    
    #Communicability angle
    df_edges['angle'] = get_angle(points, simplices)
    df_edges = df_edges.sort_values('angle', ascending=False)
    
    #Remove duplicated edges
    df_edges[['source', 'target']] = df_edges[['source', 'target']].T.apply(sorted).T
    df_edges = df_edges.drop_duplicates(subset=['source', 'target'], keep='first')

    #Distance between regions
    edges = points[df_edges[['source', 'target']]]
    df_edges['dist'] = np.linalg.norm(edges[:, 1]-edges[:, 0], axis=1)
    
    thresholds = get_thresholds(df_edges[['angle', 'dist']], points)
    df_edges['isNeighbor'] = np.all(df_edges[['angle', 'dist']] <= thresholds, axis=1)
    return df_edges, thresholds

def neighbors_graph(points, coords=True, with_thresholds=False):
    df_edges, thresholds = edgeprops(points)
    edges = np.array(df_edges[['source', 'target']][df_edges['isNeighbor']])
    if coords:
        edges = points[edges]

    if with_thresholds:
        return edges, thresholds    
    
    return edges

def plot_layout(points, **kwargs):
    return plotting.plot_layout(points, **kwargs)

def plot_neighbors_graph(points, edges, **kwargs):
    return plotting.plot_neighbors_graph(points, edges, **kwargs)

def plot_overlap(img, points, edges, **kwargs):
    return plotting.plot_overlap(img, points, edges, **kwargs)
