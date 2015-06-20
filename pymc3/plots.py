import numpy as np
from scipy.stats import kde
from .stats import *
from numpy.linalg import LinAlgError

__all__ = ['traceplot', 'kdeplot', 'kde2plot', 'forestplot', 'autocorrplot']


def traceplot(trace, vars=None, figsize=None,
              lines=None, combined=False, grid=True, 
              alpha=0.35, ax=None):
    """Plot samples histograms and values

    Parameters
    ----------

    trace : result of MCMC run
    vars : list of variable names
        Variables to be plotted, if None all variable are plotted
    figsize : figure size tuple
        If None, size is (12, num of variables * 2) inch
    lines : dict
        Dictionary of variable name / value  to be overplotted as vertical
        lines to the posteriors and horizontal lines on sample values
        e.g. mean of posteriors, true values of a simulation
    combined : bool
        Flag for combining multiple chains into a single chain. If False
        (default), chains will be plotted separately.
    grid : bool
        Flag for adding gridlines to histogram. Defaults to True.
    ax : axes
        Matplotlib axes. Defaults to None.

    Returns
    -------

    ax : matplotlib axes

    """
    import matplotlib.pyplot as plt
    if vars is None:
        vars = trace.varnames

    n = len(vars)

    if figsize is None:
        figsize = (12, n*2)

    if ax is None:
        fig, ax = plt.subplots(n, 2, squeeze=False, figsize=figsize)
    elif ax.shape != (n,2):
        print('traceplot requires n*2 subplots')
        return None

    for i, v in enumerate(vars):
        for d in trace.get_values(v, combine=combined, squeeze=False):
            d = np.squeeze(d)
            d = make_2d(d)
            if d.dtype.kind == 'i':
                histplot_op(ax[i, 0], d, alpha=alpha)
            else:
                kdeplot_op(ax[i, 0], d)
            ax[i, 0].set_title(str(v))
            ax[i, 0].grid(grid)
            ax[i, 1].set_title(str(v))
            ax[i, 1].plot(d, alpha=alpha)

            ax[i, 0].set_ylabel("Frequency")
            ax[i, 1].set_ylabel("Sample value")

            if lines:
                try:
                    ax[i, 0].axvline(x=lines[v], color="r", lw=1.5)
                    ax[i, 1].axhline(y=lines[v], color="r", lw=1.5, alpha=alpha)
                except KeyError:
                    pass

    plt.tight_layout()
    return ax

def histplot_op(ax, data, alpha=.35):
    for i in range(data.shape[1]):
        d = data[:, i]

        mind = np.min(d)
        maxd = np.max(d)
        step = max((maxd-mind)//100, 1)
        ax.hist(d, bins=range(mind, maxd + 2, step), alpha=alpha, align='left')
        ax.set_xlim(mind - .5, maxd + .5)

def kdeplot_op(ax, data):
    errored = []
    for i in range(data.shape[1]):
        d = data[:, i]
        try:
            density = kde.gaussian_kde(d)
            l = np.min(d)
            u = np.max(d)
            x = np.linspace(0, 1, 100) * (u - l) + l

            ax.plot(x, density(x))

        except LinAlgError:
            errored.append(i)

    if errored:
        ax.text(.27,.47, 'WARNING: KDE plot failed for: ' + str(errored), style='italic',
                        bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})

def make_2d(a):
    """Ravel the dimensions after the first.
    """
    a = np.atleast_2d(a.T).T
    #flatten out dimensions beyond the first
    n = a.shape[0]
    newshape = np.product(a.shape[1:]).astype(int)
    a = a.reshape((n, newshape), order='F')
    return a


def kde2plot_op(ax, x, y, grid=200):
    xmin = x.min()
    xmax = x.max()
    ymin = y.min()
    ymax = y.max()

    grid = grid * 1j
    X, Y = np.mgrid[xmin:xmax:grid, ymin:ymax:grid]
    positions = np.vstack([X.ravel(), Y.ravel()])
    values = np.vstack([x, y])
    kernel = kde.gaussian_kde(values)
    Z = np.reshape(kernel(positions).T, X.shape)

    ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,
              extent=[xmin, xmax, ymin, ymax])


def kdeplot(data, ax=None):
    if ax is None:
        f, ax = subplots(1, 1, squeeze=True)
    kdeplot_op(ax, data)
    return ax


def kde2plot(x, y, grid=200, ax=None):
    if ax is None:
        f, ax = subplots(1, 1, squeeze=True)
    kde2plot_op(ax, x, y, grid)
    return ax


def autocorrplot(trace, vars=None, max_lag=100, burn=0, ax=None):
    """Bar plot of the autocorrelation function for a trace

    Parameters
    ----------

    trace : result of MCMC run
    vars : list of variable names
        Variables to be plotted, if None all variable are plotted
    max_lag : int
        Maximum lag to calculate autocorrelation. Defaults to 100.
    burn : int
        Number of samples to discard from the beginning of the trace. 
        Defaults to 0.
    ax : axes
        Matplotlib axes. Defaults to None.
        
    Returns
    -------

    ax : matplotlib axes

    """
    
    import matplotlib.pyplot as plt

    if vars is None:
        vars = trace.varnames
    else:
        vars = [str(var) for var in vars]

    chains = trace.nchains

    fig, ax = plt.subplots(len(vars), chains, squeeze=False)

    max_lag = min(len(trace) - 1, max_lag)

    for i, v in enumerate(vars):
        for j in range(chains):
            d = np.squeeze(trace.get_values(v, chains=[j], burn=burn,
                                            combine=False))

            ax[i, j].acorr(d, detrend=plt.mlab.detrend_mean, maxlags=max_lag)

            if not j:
                ax[i, j].set_ylabel("correlation")
            ax[i, j].set_xlabel("lag")

            if chains > 1:
                ax[i, j].set_title("chain {0}".format(j+1))
    
    return (fig, ax)


def var_str(name, shape):
    """Return a sequence of strings naming the element of the tallyable object.
    This is a support function for forestplot.

    :Example:
    >>> var_str('theta', (4,))
    ['theta[1]', 'theta[2]', 'theta[3]', 'theta[4]']

    """

    size = np.prod(shape)
    ind = (np.indices(shape) + 1).reshape(-1, size)
    names = ['[' + ','.join(map(str, i)) + ']' for i in zip(*ind)]
    # if len(name)>12:
    #     name = '\n'.join(name.split('_'))
    #     name += '\n'
    names[0] = '%s %s' % (name, names[0])
    return names


def forestplot(trace_obj, vars=None, alpha=0.05, quartiles=True, rhat=True,
               main=None, xtitle=None, xrange=None, ylabels=None,
               chain_spacing=0.05, vline=0, gs=None):
    """ Forest plot (model summary plot)

    Generates a "forest plot" of 100*(1-alpha)% credible intervals for either
    the set of variables in a given model, or a specified set of nodes.

    :Arguments:
        trace_obj: NpTrace or MultiTrace object
            Trace(s) from an MCMC sample.

        vars: list
            List of variables to plot (defaults to None, which results in all
            variables plotted).

        alpha (optional): float
            Alpha value for (1-alpha)*100% credible intervals (defaults to
            0.05).

        quartiles (optional): bool
            Flag for plotting the interquartile range, in addition to the
            (1-alpha)*100% intervals (defaults to True).

        rhat (optional): bool
            Flag for plotting Gelman-Rubin statistics. Requires 2 or more
            chains (defaults to True).

        main (optional): string
            Title for main plot. Passing False results in titles being
            suppressed; passing None (default) results in default titles.

        xtitle (optional): string
            Label for x-axis. Defaults to no label

        xrange (optional): list or tuple
            Range for x-axis. Defaults to matplotlib's best guess.

        ylabels (optional): list or array
            User-defined labels for each variable. If not provided, the node
            __name__ attributes are used.

        chain_spacing (optional): float
            Plot spacing between chains (defaults to 0.05).

        vline (optional): numeric
            Location of vertical reference line (defaults to 0).
            
        gs : GridSpec
            Matplotlib GridSpec object. Defaults to None.
            
        Returns
        -------

        gs : matplotlib GridSpec

    """
    import matplotlib.pyplot as plt
    from matplotlib import gridspec

    # Quantiles to be calculated
    qlist = [100 * alpha / 2, 50, 100 * (1 - alpha / 2)]
    if quartiles:
        qlist = [100 * alpha / 2, 25, 50, 75, 100 * (1 - alpha / 2)]

    # Range for x-axis
    plotrange = None

    # Number of chains
    chains = None

    # Subplots
    interval_plot = None
    rhat_plot = None

    nchains = trace_obj.nchains
    if nchains > 1:
        from .diagnostics import gelman_rubin

        R = gelman_rubin(trace_obj)
        if vars is not None:
            R = {v: R[v] for v in vars}
    else:
        # Can't calculate Gelman-Rubin with a single trace
        rhat = False

    if vars is None:
        vars = trace_obj.varnames

    # Empty list for y-axis labels
    labels = []

    if gs is None:
        # Initialize plot
        if rhat and nchains > 1:
            gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])

        else:

            gs = gridspec.GridSpec(1, 1)

        # Subplot for confidence intervals
        interval_plot = plt.subplot(gs[0])


    trace_quantiles = quantiles(trace_obj, qlist, squeeze=False)
    hpd_intervals = hpd(trace_obj, alpha, squeeze=False)

    for j, chain in enumerate(trace_obj.chains):
        # Counter for current variable
        var = 1
        for varname in vars:
            var_quantiles = trace_quantiles[chain][varname]

            quants = [var_quantiles[v] for v in qlist]
            var_hpd = hpd_intervals[chain][varname].T

            # Substitute HPD interval for quantile
            quants[0] = var_hpd[0].T
            quants[-1] = var_hpd[1].T

            # Ensure x-axis contains range of current interval
            if plotrange:
                plotrange = [min(
                             plotrange[0],
                             np.min(quants)),
                             max(plotrange[1],
                                 np.max(quants))]
            else:
                plotrange = [np.min(quants), np.max(quants)]

            # Number of elements in current variable
            value = trace_obj.get_values(varname, chains=[chain])[0]
            k = np.size(value)

            # Append variable name(s) to list
            if not j:
                if k > 1:
                    names = var_str(varname, np.shape(value))
                    labels += names
                else:
                    labels.append(varname)
                    # labels.append('\n'.join(varname.split('_')))

            # Add spacing for each chain, if more than one
            e = [0] + [(chain_spacing * ((i + 2) / 2)) *
                       (-1) ** i for i in range(nchains - 1)]

            # Deal with multivariate nodes
            if k > 1:

                for i, q in enumerate(np.transpose(quants).squeeze()):

                    # Y coordinate with jitter
                    y = -(var + i) + e[j]

                    if quartiles:
                        # Plot median
                        plt.plot(q[2], y, 'bo', markersize=4)
                        # Plot quartile interval
                        plt.errorbar(
                            x=(q[1],
                                q[3]),
                            y=(y,
                                y),
                            linewidth=2,
                            color='b')

                    else:
                        # Plot median
                        plt.plot(q[1], y, 'bo', markersize=4)

                    # Plot outer interval
                    plt.errorbar(
                        x=(q[0],
                            q[-1]),
                        y=(y,
                            y),
                        linewidth=1,
                        color='b')

            else:

                # Y coordinate with jitter
                y = -var + e[j]

                if quartiles:
                    # Plot median
                    plt.plot(quants[2], y, 'bo', markersize=4)
                    # Plot quartile interval
                    plt.errorbar(
                        x=(quants[1],
                            quants[3]),
                        y=(y,
                            y),
                        linewidth=2,
                        color='b')
                else:
                    # Plot median
                    plt.plot(quants[1], y, 'bo', markersize=4)

                # Plot outer interval
                plt.errorbar(
                    x=(quants[0],
                        quants[-1]),
                    y=(y,
                        y),
                    linewidth=1,
                    color='b')

            # Increment index
            var += k

    labels = ylabels if ylabels is not None else labels

    # Update margins
    left_margin = np.max([len(x) for x in labels]) * 0.015
    gs.update(left=left_margin, right=0.95, top=0.9, bottom=0.05)

    # Define range of y-axis
    plt.ylim(-var + 0.5, -0.5)

    datarange = plotrange[1] - plotrange[0]
    plt.xlim(plotrange[0] - 0.05 * datarange, plotrange[1] + 0.05 * datarange)

    # Add variable labels
    plt.yticks([-(l + 1) for l in range(len(labels))], labels)

    # Add title
    if main is not False:
        plot_title = main or str(int((
            1 - alpha) * 100)) + "% Credible Intervals"
        plt.title(plot_title)

    # Add x-axis label
    if xtitle is not None:
        plt.xlabel(xtitle)

    # Constrain to specified range
    if xrange is not None:
        plt.xlim(*xrange)

    # Remove ticklines on y-axes
    for ticks in interval_plot.yaxis.get_major_ticks():
        ticks.tick1On = False
        ticks.tick2On = False

    for loc, spine in interval_plot.spines.items():
        if loc in ['bottom', 'top']:
            pass
            # spine.set_position(('outward',10)) # outward by 10 points
        elif loc in ['left', 'right']:
            spine.set_color('none')  # don't draw spine

    # Reference line
    plt.axvline(vline, color='k', linestyle='--')

    # Genenerate Gelman-Rubin plot
    if rhat and nchains > 1:

        # If there are multiple chains, calculate R-hat
        rhat_plot = plt.subplot(gs[1])

        if main is not False:
            plt.title("R-hat")

        # Set x range
        plt.xlim(0.9, 2.1)

        # X axis labels
        plt.xticks((1.0, 1.5, 2.0), ("1", "1.5", "2+"))
        plt.yticks([-(l + 1) for l in range(len(labels))], "")

        i = 1
        for varname in vars:

            chain = trace_obj.chains[0]
            value = trace_obj.get_values(varname, chains=[chain])[0]
            k = np.size(value)

            if k > 1:
                plt.plot([min(r, 2) for r in R[varname]], [-(j + i)
                     for j in range(k)], 'bo', markersize=4)
            else:
                plt.plot(min(R[varname], 2), -i, 'bo', markersize=4)

            i += k

        # Define range of y-axis
        plt.ylim(-i + 0.5, -0.5)

        # Remove ticklines on y-axes
        for ticks in rhat_plot.yaxis.get_major_ticks():
            ticks.tick1On = False
            ticks.tick2On = False

        for loc, spine in rhat_plot.spines.items():
            if loc in ['bottom', 'top']:
                pass
                # spine.set_position(('outward',10)) # outward by 10 points
            elif loc in ['left', 'right']:
                spine.set_color('none')  # don't draw spine

    return gs
