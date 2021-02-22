import numpy as np
import json
import os
from tqdm import tqdm
from random import choice
from sklearn.cluster import KMeans
from time import time
import warnings
from math import sqrt

from sklearn.utils import check_random_state, check_array
from sklearn.utils.extmath import randomized_svd, safe_sparse_dot, squared_norm
from sklearn.utils.validation import check_is_fitted, check_non_negative
from ..database_utils.utils import decoding_categories, encoding_categories
from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import json_load_data, json_save_data 

def norm(x):
    """Dot product-based Euclidean norm implementation.
    See: http://fseoane.net/blog/2011/computing-the-vector-norm/
    Parameters
    ----------
    x : array-like
        Vector for which to compute the norm.
    """
    return sqrt(squared_norm(x))

def _initialize_nmf(X, n_components, init='warn', eps=1e-6,
                    random_state=None):
    """Algorithms for NMF initialization.
    Computes an initial guess for the non-negative
    rank k matrix approximation for X: X = WH.
    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        The data matrix to be decomposed.
    n_components : int
        The number of components desired in the approximation.
    init :  {'random', 'nndsvd', 'nndsvda', 'nndsvdar'}, default=None
        Method used to initialize the procedure.
        Default: None.
        Valid options:
        - None: 'nndsvd' if n_components <= min(n_samples, n_features),
            otherwise 'random'.
        - 'random': non-negative random matrices, scaled with:
            sqrt(X.mean() / n_components)
        - 'nndsvd': Nonnegative Double Singular Value Decomposition (NNDSVD)
            initialization (better for sparseness)
        - 'nndsvda': NNDSVD with zeros filled with the average of X
            (better when sparsity is not desired)
        - 'nndsvdar': NNDSVD with zeros filled with small random values
            (generally faster, less accurate alternative to NNDSVDa
            for when sparsity is not desired)
        - 'custom': use custom matrices W and H
    eps : float, default=1e-6
        Truncate all values less then this in output to zero.
    random_state : int, RandomState instance or None, default=None
        Used when ``init`` == 'nndsvdar' or 'random'. Pass an int for
        reproducible results across multiple function calls.
        See :term:`Glossary <random_state>`.
    Returns
    -------
    W : array-like of shape (n_samples, n_components)
        Initial guesses for solving X ~= WH.
    H : array-like of shape (n_components, n_features)
        Initial guesses for solving X ~= WH.
    References
    ----------
    C. Boutsidis, E. Gallopoulos: SVD based initialization: A head start for
    nonnegative matrix factorization - Pattern Recognition, 2008
    http://tinyurl.com/nndsvd
    """
    if init == 'warn':
        warnings.warn(("The 'init' value, when 'init=None' and "
                       "n_components is less than n_samples and "
                       "n_features, will be changed from 'nndsvd' to "
                       "'nndsvda' in 1.1 (renaming of 0.26)."), FutureWarning)
        init = None

    check_non_negative(X, "NMF initialization")
    n_samples, n_features = X.shape

    if (init is not None and init != 'random'
            and n_components > min(n_samples, n_features)):
        raise ValueError("init = '{}' can only be used when "
                         "n_components <= min(n_samples, n_features)"
                         .format(init))

    if init is None:
        if n_components <= min(n_samples, n_features):
            init = 'nndsvd'
        else:
            init = 'random'

    # Random initialization
    if init == 'random':
        avg = np.sqrt(X.mean() / n_components)
        rng = check_random_state(random_state)
        H = avg * rng.randn(n_components, n_features).astype(X.dtype,
                                                             copy=False)
        W = avg * rng.randn(n_samples, n_components).astype(X.dtype,
                                                            copy=False)
        np.abs(H, out=H)
        np.abs(W, out=W)
        return W, H

    # NNDSVD initialization
    U, S, V = randomized_svd(X, n_components, random_state=random_state)
    W = np.zeros_like(U)
    H = np.zeros_like(V)

    # The leading singular triplet is non-negative
    # so it can be used as is for initialization.
    W[:, 0] = np.sqrt(S[0]) * np.abs(U[:, 0])
    H[0, :] = np.sqrt(S[0]) * np.abs(V[0, :])

    for j in range(1, n_components):
        x, y = U[:, j], V[j, :]

        # extract positive and negative parts of column vectors
        x_p, y_p = np.maximum(x, 0), np.maximum(y, 0)
        x_n, y_n = np.abs(np.minimum(x, 0)), np.abs(np.minimum(y, 0))

        # and their norms
        x_p_nrm, y_p_nrm = norm(x_p), norm(y_p)
        x_n_nrm, y_n_nrm = norm(x_n), norm(y_n)

        m_p, m_n = x_p_nrm * y_p_nrm, x_n_nrm * y_n_nrm

        # choose update
        if m_p > m_n:
            u = x_p / x_p_nrm
            v = y_p / y_p_nrm
            sigma = m_p
        else:
            u = x_n / x_n_nrm
            v = y_n / y_n_nrm
            sigma = m_n

        lbd = np.sqrt(S[j] * sigma)
        W[:, j] = lbd * u
        H[j, :] = lbd * v

    W[W < eps] = 0
    H[H < eps] = 0

    if init == "nndsvd":
        pass
    elif init == "nndsvda":
        avg = X.mean()
        W[W == 0] = avg
        H[H == 0] = avg
    elif init == "nndsvdar":
        rng = check_random_state(random_state)
        avg = X.mean()
        W[W == 0] = abs(avg * rng.randn(len(W[W == 0])) / 100)
        H[H == 0] = abs(avg * rng.randn(len(H[H == 0])) / 100)
    else:
        raise ValueError(
            'Invalid init parameter: got %r instead of one of %r' %
            (init, (None, 'random', 'nndsvd', 'nndsvda', 'nndsvdar')))

    return W, H

def DTPP(V, k1, k2):
    c = CoClustering(k1, k2, 0)
    #init
    # W, H = _initialize_nmf(V, k1, init="nndsvd")
    # W = c.random_orthonormal_matrix(V.shape[0], k1)
    # H = c.random_orthonormal_matrix(V.shape[1], k2).T
    W, H = c._fit(V)
    

    # S = np.linalg.pinv(W).dot(V).dot(np.linalg.pinv(H))
    S = W.T.dot(V).dot(H.T)

    ################ matlab version ###################
    # W = W .* sqrt( (V*H'*S') ./ max(W*W'*V*H'*S', options.myeps) );
    # H = H .* sqrt( (S'*W'*V) ./ max(S'*W'*V*(H'*H), options.myeps) );
    # S = S .* sqrt( (W'*V*H') ./ (W'*W*S*(H*H')));
    # S = max(S, eps);

    for i in range(100):
        err = V - W.dot(S).dot(H)
        err = (err**2).sum()
        err2 = (W.T.dot(V).dot(H.T) - S)**2
        err2 = err2.sum()
        print("iter: {}, err: {}, err2: {}".format(i, err, err2))
        W = W * np.sqrt(V.dot(H.T).dot(S.T) \
            / np.maximum(W.dot(W.T).dot(V).dot(H.T).dot(S.T), 1e-16))
        H = H * np.sqrt(S.T.dot(W.T).dot(V) \
            / np.maximum(S.T.dot(W.T).dot(V).dot(np.dot(H.T, H)), 1e-16))
        S = S * np.sqrt(W.T.dot(V).dot(H.T) / W.T.dot(W).dot(S).dot(np.dot(H, H.T)))
        S = np.maximum(S, 1e-16)
    
    _S = W.T.dot(V).dot(H.T)
    err = np.abs(_S - S)

    a =  1


class CoClustering(object):
    def __init__(self, k1, k2, w_t = 1, n_iter=100):
        self.w_t = w_t
        self.k1 = k1
        self.k2 = k2
        self.n_iter = n_iter

    def kmeans(self, M, k):
        kmeans = KMeans(n_clusters=k, random_state=12).fit(M)
        cluster = kmeans.labels_
        res = np.zeros((M.shape[0], k))
        res[np.array(range(M.shape[0])), cluster] = 1
        return res

    def eigenvector(self, M, k):
        eigenvalues, eigenvectors = np.linalg.eig(M)
        idx = eigenvalues.argsort()[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        real = eigenvectors.real
        imag = eigenvectors.imag
        # assert (imag ** 2).sum() < 1e-6
        # print("image sum ", (imag ** 2).sum())
        return eigenvectors[:, :k]

    def random_orthonormal_matrix(self, n, k):
        M = np.zeros((n, k))
        cluster = np.random.randint(0, k, n)
        M[np.array(range(n)), cluster] = 1
        norm = M.sum(axis=0) ** 0.5
        norm = norm.reshape(1,-1)
        M = M / norm
        return M

    def _fit(self, R, text_feature=None):
        # init 
        k1 = self.k1
        k2 = self.k2
        k = min(k1, k2)
        n1, n2 = R.shape
        C1 = self.random_orthonormal_matrix(n1, k)
        C2 = self.random_orthonormal_matrix(n2, k)
        pre_C1 = C1.copy()
        pre_C2 = C2.copy()
        if text_feature is not None:
            text_part = self.w_t * np.dot(text_feature, text_feature.T)
        else:
            text_part = 0
        for i in range(self.n_iter):
            t0 = time()
            tmp = np.dot(R, C2)
            tmp = np.dot(tmp, C2.T)
            M1 = np.dot(tmp, R.T) + text_part
            C1 = self.eigenvector(M1, k)

            tmp = np.dot(R.T, C1)
            tmp = np.dot(tmp, C1.T)
            M2 = np.dot(tmp, R)
            C2 = self.eigenvector(M2, k)

            trr1 = C1.T.dot(R).dot(C2).dot(C2.T).dot(R.T).dot(C1).trace()
            trr2 = C2.T.dot(R.T).dot(C1).dot(C1.T).dot(R).dot(C2).trace()
            err1 = ((C1 - pre_C1)**2).sum()
            err2 = ((C2 - pre_C2)**2).sum()
            print("iter {}, time cost: {}, err1: {}, err2: {},\n trr1: {}, trr2: {}" \
                .format(i, time() - t0, err1, err2, trr1, trr2))
            pre_C1 = C1.copy()
            pre_C2 = C2.copy()
            pre_M1 = M1.copy()
        print("C1 imag", (abs(C1.imag)).sum())
        print("C2 imag", (abs(C2.imag)).sum())
        W = C1.real
        H = C2.real.T
        return W, H

    def fit(self, R, text_feature=None):
        W, H = self._fit(R, text_feature)
        S = W.T.dot(R).dot(H.T)
        err = R - W.dot(S).dot(H)
        err = (err**2).sum()
        C1 = self.kmeans(W, self.k1)
        C2 = self.kmeans(H.T, self.k2)
        return C1, C2
        
    def rearrange(self, R, C1, C2):
        n1, k1 = C1.shape
        n2, k2 = C2.shape
        cls1 = np.array(range(k1)).reshape(1, -1).repeat(axis=0, repeats=n1)
        cls2 = np.array(range(k2)).reshape(1, -1).repeat(axis=0, repeats=n2)
        cls1 = (C1 * cls1).sum(axis=1)
        cls2 = (C2 * cls2).sum(axis=1)
        idx1 = cls1.argsort()
        idx2 = cls2.argsort()
        R = R[idx1, :]
        R = R[:, idx2]
        return R
