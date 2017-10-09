import numpy as np
from scipy.signal import gaussian, convolve

try:
    import matplotlib.pyplot as plt
except ImportError:  # mpl is optional
    pass


def kdeplot(values, label=None, shade=0, ax=None, kwargs_shade=None, **kwargs):
    """
    1D KDE plot taking into account boundary conditions

    Parameters
    ----------
    values : array-like
        Values to plot
    label : string
        Text to include as part of the legend
    shade : float
        Alpha blending value for the shaded area under the curve, between 0
        (no shade) and 1 (opaque). Defaults to 0
    ax : matplotlib axes
    kwargs_shade : dicts, optional
        Additional keywords passed to `matplotlib.axes.Axes.fill_between`
        (to control the shade)
    Returns
    ----------
    ax : matplotlib axes

    """
    if ax is None:
        _, ax = plt.subplots()

    if kwargs_shade is None:
        kwargs_shade = {}

    density, l, u = fast_kde(values)
    x = np.linspace(l, u, len(density))
    ax.plot(x, density, label=label, **kwargs)
    ax.set_ylim(0)
    if shade:
        ax.fill_between(x, density, alpha=shade, **kwargs_shade)
    return ax


def fast_kde(x):
    """
    A fft-based Gaussian kernel density estimate (KDE) for computing
    the KDE on a regular grid.
    The code was adapted from https://github.com/mfouesneau/faststats

    Parameters
    ----------

    x : Numpy array or list

    Returns
    -------

    grid: A gridded 1D KDE of the input points (x).
    xmin: minimum value of x
    xmax: maximum value of x

    """
    x = np.array(x, dtype=float)
    x = x[~np.isnan(x)]
    x = x[~np.isinf(x)]
    n = len(x)
    nx = 200

    # add small jitter in case input values are the same
    x += np.random.uniform(-1E-12, 1E-12, size=n)
    xmin, xmax = np.min(x), np.max(x)

    # compute histogram
    bins = np.linspace(xmin, xmax, nx)
    xyi = np.digitize(x, bins)
    dx = (xmax - xmin) / (nx - 1)
    grid = np.histogram(x, bins=nx)[0]

    # Scaling factor for bandwidth
    scotts_factor = n ** (-0.2)
    # Determine the bandwidth using Scott's rule
    std_x = np.std(xyi)
    kern_nx = int(np.round(scotts_factor * 2 * np.pi * std_x))

    # Evaluate the gaussian function on the kernel grid
    kernel = np.reshape(gaussian(kern_nx, scotts_factor * std_x), kern_nx)

    # Compute the KDE
    # use symmetric padding to correct for data boundaries in the kde
    npad = np.min((nx, 2 * kern_nx))

    grid = np.concatenate([grid[npad: 0: -1], grid, grid[nx: nx - npad: -1]])
    grid = convolve(grid, kernel, mode='same')[npad: npad + nx]

    norm_factor = n * dx * (2 * np.pi * std_x ** 2 * scotts_factor ** 2) ** 0.5

    grid = grid / norm_factor

    return grid, xmin, xmax
