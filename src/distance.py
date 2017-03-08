# trimmed down version of scipy.spatial.distance
#
# Copyright (C) Damian Eads, 2007-2008. New BSD License.


import numpy as np
from scipy.spatial import _distance_wrap


def _copy_array_if_base_present(a):
    """
    Copies the array if its base points to a parent array.
    """
    if a.base is not None:
        return a.copy()
    elif np.issubsctype(a, np.float32):
        return np.array(a, dtype=np.double)
    else:
        return a


def _convert_to_double(X):
    if X.dtype != np.double:
        X = X.astype(np.double)
    if not X.flags.contiguous:
        X = X.copy()
    return X


def cdist(XA, XB):
    """
    Computes distance between each pair of the two collections of inputs.

    The following are common calling conventions:

    1. ``Y = cdist(XA, XB, 'euclidean')``

       Computes the distance between :math:`m` points using
       Euclidean distance (2-norm) as the distance metric between the
       points. The points are arranged as :math:`m`
       :math:`n`-dimensional row vectors in the matrix X.


    Parameters
    ----------
    XA : ndarray
        An :math:`m_A` by :math:`n` array of :math:`m_A`
        original observations in an :math:`n`-dimensional space.
        Inputs are converted to float type.
    XB : ndarray
        An :math:`m_B` by :math:`n` array of :math:`m_B`
        original observations in an :math:`n`-dimensional space.
        Inputs are converted to float type.
    metric : str or callable, optional
        The distance metric to use.  If a string, the distance function can be
        'braycurtis', 'canberra', 'chebyshev', 'cityblock', 'correlation',
        'cosine', 'dice', 'euclidean', 'hamming', 'jaccard', 'kulsinski',
        'mahalanobis', 'matching', 'minkowski', 'rogerstanimoto', 'russellrao',
        'seuclidean', 'sokalmichener', 'sokalsneath', 'sqeuclidean',
        'wminkowski', 'yule'.
    w : ndarray, optional
        The weight vector (for weighted Minkowski).
    p : scalar, optional
        The p-norm to apply (for Minkowski, weighted and unweighted)
    V : ndarray, optional
        The variance vector (for standardized Euclidean).
    VI : ndarray, optional
        The inverse of the covariance matrix (for Mahalanobis).

    Returns
    -------
    Y : ndarray
        A :math:`m_A` by :math:`m_B` distance matrix is returned.
        For each :math:`i` and :math:`j`, the metric
        ``dist(u=XA[i], v=XB[j])`` is computed and stored in the
        :math:`ij` th entry.

    Raises
    ------
    ValueError
        An exception is thrown if `XA` and `XB` do not have
        the same number of columns.

    Examples
    --------
    Find the Euclidean distances between four 2-D coordinates:

    >>> from scipy.spatial import distance
    >>> coords = [(35.0456, -85.2672),
    ...           (35.1174, -89.9711),
    ...           (35.9728, -83.9422),
    ...           (36.1667, -86.7833)]
    >>> distance.cdist(coords, coords, 'euclidean')
    array([[ 0.    ,  4.7044,  1.6172,  1.8856],
           [ 4.7044,  0.    ,  6.0893,  3.3561],
           [ 1.6172,  6.0893,  0.    ,  2.8477],
           [ 1.8856,  3.3561,  2.8477,  0.    ]])

    """

    XA = np.asarray(XA, order='c')
    XB = np.asarray(XB, order='c')

    # The C code doesn't do striding.
    XA = _copy_array_if_base_present(_convert_to_double(XA))
    XB = _copy_array_if_base_present(_convert_to_double(XB))

    s = XA.shape
    sB = XB.shape

    # if len(s) != 2:
    #     raise ValueError('XA must be a 2-dimensional array.')
    # if len(sB) != 2:
    #     raise ValueError('XB must be a 2-dimensional array.')
    # if s[1] != sB[1]:
    #     raise ValueError('XA and XB must have the same number of columns '
    #                      '(i.e. feature dimension.)')

    mA = s[0]
    mB = sB[0]
    dm = np.zeros((mA, mB), dtype=np.double)
  
    cdist_fn = getattr(_distance_wrap, "cdist_euclidean_wrap")
    cdist_fn(XA, XB, dm)

    return dm
