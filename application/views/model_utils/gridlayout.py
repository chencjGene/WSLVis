import numpy as np
import os
import sys
import ctypes
import math
from time import time

from lapjv import lapjv
from scipy.spatial.distance import cdist

from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import check_dir, pickle_load_data, pickle_save_data


def grid_layout(idx, X, selected_list, selected_pos, mismatch,
                k=100, constraint_matrix = None):
    X -= X.min(axis=0)
    X /= X.max(axis=0)
    num = X.shape[0]
    square_len = math.ceil(np.sqrt(num))
    N = square_len * square_len
    grids = np.dstack(np.meshgrid(np.linspace(0, 1 - 1.0 / square_len, square_len),
            np.linspace(0, 1 - 1.0 / square_len, square_len))) \
            .reshape(-1, 2)
    # # ...
    # fake_cost_matrix = cdist(grids, X, "euclidean")
    # # knn process
    # dummy_points = np.ones((N - fake_cost_matrix.shape[1], 2)) * 0.5
    # # dummy at [0.5, 0.5]
    # dummy_vertices = (1 - cdist(grids, dummy_points, "euclidean")) * 100
    # cost_matrix = np.concatenate((fake_cost_matrix, dummy_vertices), axis=1)
    #
    # libc = ctypes.cdll.LoadLibrary(os.path.join(config.scripts_root, "c_utils.dll"))
    #
    # cost_matrix = cost_matrix.astype(np.dtype('d'))
    # rows, cols = cost_matrix.shape
    # cost_matrix_1 = np.asarray(cost_matrix.copy())
    # cost_matrix_2 = np.asarray(cost_matrix.T.copy())
    # ptr1 = cost_matrix_1.ctypes.data_as(ctypes.c_char_p)
    # ptr2 = cost_matrix_2.ctypes.data_as(ctypes.c_char_p)
    # k = min(cost_matrix.shape[0], k)
    # print("k = ", k, "is used")
    # libc.knn_sparse(ptr1, rows, cols, k, False, 0)
    # libc.knn_sparse(ptr2, cols, rows, k, False, 0)
    # cost_matrix_2 = cost_matrix_2.T
    # logger.info("end knn preprocessing")
    #
    # # merge two sub-graph
    # cost_matrix = np.maximum(cost_matrix_1, cost_matrix_2)
    #
    # # # binning
    # # cost_matrix = cost_matrix / original_cost_matrix.max() * 100
    # # cost_matrix = cost_matrix.astype(np.int32)
    # cost_matrix[cost_matrix == 0] = 10000000
    #
    # # begin LAP-JV
    # logger.info("begin LAP JV")
    # t = time()
    # row_asses, col_asses, info = lapjv(cost_matrix)
    # real_cost = fake_cost_matrix[col_asses[:num],
    #                             np.array(range(N))[:num]].sum()



    original_cost_matrix = cdist(grids, X, "euclidean")
    # knn process
    dummy_points = np.ones((N - original_cost_matrix.shape[1], 2)) * 0.5
    # dummy at [0.5, 0.5]
    dummy_vertices = (1 - cdist(grids, dummy_points, "euclidean")) * 100
    cost_matrix = np.concatenate((original_cost_matrix, dummy_vertices), axis=1)

    # libc = ctypes.cdll.LoadLibrary(os.path.join(config.scripts_root, "c_utils.dll"))
    # cost_matrix = cost_matrix.astype(np.dtype('d'))
    # rows, cols = cost_matrix.shape
    # cost_matrix_1 = np.asarray(cost_matrix.copy())
    # cost_matrix_2 = np.asarray(cost_matrix.T.copy())
    # ptr1 = cost_matrix_1.ctypes.data_as(ctypes.c_char_p)
    # ptr2 = cost_matrix_2.ctypes.data_as(ctypes.c_char_p)
    # k = min(cost_matrix.shape[0], k)
    # libc.knn_sparse(ptr1, rows, cols, k, False, 0)
    # libc.knn_sparse(ptr2, cols, rows, k, False, 0)
    # cost_matrix_2 = cost_matrix_2.T
    # logger.info("end knn preprocessing")
    # # merge two sub-graph
    # cost_matrix = np.maximum(cost_matrix_1, cost_matrix_2)

    # # # binning
    # # cost_matrix = cost_matrix / original_cost_matrix.max() * 100
    # # cost_matrix = cost_matrix.astype(np.int32)
    # cost_matrix[cost_matrix == 0] = 10000000

    if len(selected_list) > 0:
        print("*****************************constraint******************************")
        pointer = 0
        selected_mismatch = mismatch[np.array(selected_list)]
        for i, id in enumerate(selected_list):
            if pointer > len(idx):
                break
            while pointer < len(idx) and idx[pointer] < id:
                pointer += 1
            if idx[pointer] == id:
                pointer += 1
                # print(i, id, selected_pos[i])
                if selected_mismatch[i] > 0.4:
                    dis = ((grids - selected_pos[i])**2).sum(axis=1)
                    sorted_idx = dis.argsort()
                    nearest_grids = grids[sorted_idx[:25]]
                    this_position = X[pointer-1,:]
                    dis = ((nearest_grids - this_position)**2).sum(axis=1)
                    nearest_idx = sorted_idx[:25][dis.argsort()[:5]]
                    cost_matrix[nearest_idx, pointer-1] = 0.001
                    # print(nearest_idx, pointer-1, id)
                # X[pointer-1,:] = selected_pos[i]
    else:
        print("root used")


    # begin LAP-JV
    logger.info("begin LAP JV")
    t = time()
    row_asses, col_asses, info = lapjv(cost_matrix)
    col_asses = col_asses[:num]
    grid_X = grids[col_asses]
    logger.info("train cost: {}, time cost: {}"
                .format(info[0], time() - t))
    # logger.info("train cost: {}, time cost: {}, real_cost: {}, cost delta: {}"
    #             .format(cost, time() - t, real_cost, (cost - real_cost)/real_cost))

    return grid_X, row_asses, col_asses