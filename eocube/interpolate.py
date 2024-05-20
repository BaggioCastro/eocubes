
import numba as nb
import numpy as np


@nb.njit
def nan_helper_numba(y, cloud):
    return (cloud > 7) | (cloud <= 3) | (y>10000) | (y<-10000), lambda z: z.nonzero()[0]

@nb.njit
def interpolate_vec_numba(x, cloud):
    nans, idx = nan_helper_numba(x, cloud)
    try:
        x[nans] = np.interp(idx(nans), idx(~nans), x[~nans])
        return x
    except:
        return x

@nb.njit(parallel=True)
def interpolate_mtx_numba(mtx, cloud):
    nrows, ncols = mtx.shape
    mtx_interpolated = np.empty_like(mtx)

    for i in nb.prange(nrows):
        mtx_interpolated[i, :] = interpolate_vec_numba(mtx[i, :], cloud[i, :])

    return mtx_interpolated
