import numpy as np

def reshape_simp(simplices):
    """Decomposition of tetrahedrons in triangles"""
    N = simplices.shape[0]
    idx = np.array([[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]])
    simplices = simplices[:, idx].reshape((N*4, 3))
    return simplices

    
def simp2edge(simplices):
    """Get edges from simplices"""
    N = simplices.shape[0]
    size = 3*N
    idx = np.array([[0, 1], [0, 2], [1, 2]])
    return simplices[:, idx].reshape((size, 2))


def simp_permutations(simplices):
    """Compute all triangles given a set of simplices"""
    N = len(simplices)    
    size = 3*N
    idx = np.array([[0, 1, 2], [0, 2, 1], [1, 2, 0]])
    perm = simplices[:, idx]
    A = perm[:, :, 0].reshape(size)
    B = perm[:, :, 1].reshape(size)
    C = perm[:, :, 2].reshape(size)
    return A, B, C


def normalized_vector(x):
    if len(x.shape)>1:
        x_norm = np.linalg.norm(x, axis=1)
        return (x.T/x_norm).T
    
    return x/np.linalg.norm(x)
  