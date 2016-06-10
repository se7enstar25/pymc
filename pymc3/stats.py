"""Statistical utility functions for PyMC"""

import numpy as np
import pandas as pd
import itertools
import sys
import warnings
from .model import modelcontext

from scipy.stats.distributions import pareto

from .backends import tracetab as ttab

__all__ = ['autocorr', 'autocov', 'dic', 'bpic', 'waic', 'loo', 'hpd', 'quantiles', 
            'mc_error', 'summary', 'df_summary']

def statfunc(f):
    """
    Decorator for statistical utility function to automatically
    extract the trace array from whatever object is passed.
    """

    def wrapped_f(pymc3_obj, *args, **kwargs):
        try:
            vars = kwargs.pop('vars',  pymc3_obj.varnames)
            chains = kwargs.pop('chains', pymc3_obj.chains)
        except AttributeError:
            # If fails, assume that raw data was passed.
            return f(pymc3_obj, *args, **kwargs)

        burn = kwargs.pop('burn', 0)
        thin = kwargs.pop('thin', 1)
        combine = kwargs.pop('combine', False)
        ## Remove outer level chain keys if only one chain)
        squeeze = kwargs.pop('squeeze', True)

        results = {chain: {} for chain in chains}
        for var in vars:
            samples = pymc3_obj.get_values(var, chains=chains, burn=burn,
                                          thin=thin, combine=combine,
                                          squeeze=False)
            for chain, data in zip(chains, samples):
                results[chain][var] = f(np.squeeze(data), *args, **kwargs)

        if squeeze and (len(chains) == 1 or combine):
            results = results[chains[0]]
        return results

    wrapped_f.__doc__ = f.__doc__
    wrapped_f.__name__ = f.__name__

    return wrapped_f

@statfunc
def autocorr(x, lag=1):
    """Sample autocorrelation at specified lag.
    The autocorrelation is the correlation of x_i with x_{i+lag}.
    """

    S = autocov(x, lag)
    return S[0, 1]/np.sqrt(np.prod(np.diag(S)))

@statfunc
def autocov(x, lag=1):
    """
    Sample autocovariance at specified lag.
    The autocovariance is a 2x2 matrix with the variances of
    x[:-lag] and x[lag:] in the diagonal and the autocovariance
    on the off-diagonal.
    """
    x = np.asarray(x)

    if not lag: return 1
    if lag < 0:
        raise ValueError("Autocovariance lag must be a positive integer")
    return np.cov(x[:-lag], x[lag:], bias=1)

def dic(trace, model=None):
    """
    Calculate the deviance information criterion of the samples in trace from model
    Read more theory here - in a paper by some of the leading authorities on Model Selection - http://bit.ly/1W2YJ7c
    """
    model = modelcontext(model)

    mean_deviance = -2 * np.mean([model.logp(pt) for pt in trace])

    free_rv_means = {rv.name: trace[rv.name].mean(axis=0) for rv in model.free_RVs}
    deviance_at_mean = -2 * model.logp(free_rv_means)

    return 2 * mean_deviance - deviance_at_mean
    
def log_post_trace(trace, model):
    '''
    Calculate the elementwise log-posterior for the sampled trace.
    '''
    return np.hstack([obs.logp_elemwise(pt) for pt in trace] for obs in model.observed_RVs)

def waic(trace, model=None):
    """
    Calculate the widely available information criterion and the effective number of parameters of the samples in trace from model.
    Read more theory here - in a paper by some of the leading authorities on Model Selection - http://bit.ly/1W2YJ7c
    """
    model = modelcontext(model)
    
    log_py = log_post_trace(trace, model)

    lppd =  np.sum(np.log(np.mean(np.exp(log_py), axis=0)))
        
    p_waic = np.sum(np.var(log_py, axis=0))
    
    return -2 * lppd + 2 * p_waic, p_waic
    
def loo(trace, model=None):
    """
    Calculates leave-one-out (LOO) cross-validation for out of sample predictive
    model fit, following Vehtari et al. (2015). Cross-validation is computed using
    Pareto-smoothed importance sampling (PSIS).
    
    Returns log pointwise predictive density calculated via approximated LOO cross-validation.
    """
    model = modelcontext(model)
    
    log_py = log_post_trace(trace, model)
    
    # Importance ratios
    r = 1./np.exp(log_py)
    r_sorted = np.sort(r, axis=0)

    # Extract largest 20% of importance ratios and fit generalized Pareto to each 
    # (returns tuple with shape, location, scale)
    q80 = int(len(log_py)*0.8)
    pareto_fit = np.apply_along_axis(lambda x: pareto.fit(x, floc=0), 0, r_sorted[q80:])
    
    if np.any(pareto_fit[0] > 0.5):
        warnings.warn("""Estimated shape parameter of Pareto distribution
        is for one or more samples is greater than 0.5. This may indicate
        that the variance of the Pareto smoothed importance sampling estimate 
        is very large.""")
    
    # Calculate expected values of the order statistics of the fitted Pareto
    S = len(r_sorted)
    M = S - q80
    z = (np.arange(M)+0.5)/M
    expvals = map(lambda x: pareto.ppf(z, x[0], scale=x[2]), pareto_fit.T)
    
    # Replace importance ratios with order statistics of fitted Pareto
    r_sorted[q80:] = np.vstack(expvals).T
    # Unsort ratios (within columns) before using them as weights
    r_new = np.array([r[np.argsort(i)] for r,i in zip(r_sorted, np.argsort(r, axis=0))])
    
    # Truncate weights to guarantee finite variance
    w = np.minimum(r_new, r_new.mean(axis=0) * S**0.75)
    
    loo_lppd = np.sum(np.log(np.sum(w * np.exp(log_py), axis=0) / np.sum(w, axis=0)))
    
    return loo_lppd
    

def bpic(trace, model=None):
    """
    Calculates Bayesian predictive information criterion n of the samples in trace from model
    Read more theory here - in a paper by some of the leading authorities on Model Selection - http://bit.ly/1W2YJ7c
    """
    model = modelcontext(model)

    mean_deviance = -2 * np.mean([model.logp(pt) for pt in trace])

    free_rv_means = {rv.name: trace[rv.name].mean(axis=0) for rv in model.free_RVs}
    deviance_at_mean = -2 * model.logp(free_rv_means)

    return 3 * mean_deviance - 2 * deviance_at_mean

def make_indices(dimensions):
    # Generates complete set of indices for given dimensions

    level = len(dimensions)

    if level == 1: return list(range(dimensions[0]))

    indices = [[]]

    while level:

        _indices = []

        for j in range(dimensions[level-1]):

            _indices += [[j]+i for i in indices]

        indices = _indices

        level -= 1

    try:
        return [tuple(i) for i in indices]
    except TypeError:
        return indices

def calc_min_interval(x, alpha):
    """Internal method to determine the minimum interval of
    a given width

    Assumes that x is sorted numpy array.
    """

    n = len(x)
    cred_mass = 1.0-alpha

    interval_idx_inc = int(np.floor(cred_mass*n))
    n_intervals = n - interval_idx_inc
    interval_width = x[interval_idx_inc:] - x[:n_intervals]

    if len(interval_width) == 0:
        raise ValueError('Too few elements for interval calculation')

    min_idx = np.argmin(interval_width)
    hdi_min = x[min_idx]
    hdi_max = x[min_idx+interval_idx_inc]
    return hdi_min, hdi_max

@statfunc
def hpd(x, alpha=0.05):
    """Calculate highest posterior density (HPD) of array for given alpha. The HPD is the
    minimum width Bayesian credible interval (BCI).

    :Arguments:
      x : Numpy array
          An array containing MCMC samples
      alpha : float
          Desired probability of type I error (defaults to 0.05)

    """

    # Make a copy of trace
    x = x.copy()

    # For multivariate node
    if x.ndim > 1:

        # Transpose first, then sort
        tx = np.transpose(x, list(range(x.ndim))[1:]+[0])
        dims = np.shape(tx)

        # Container list for intervals
        intervals = np.resize(0.0, dims[:-1]+(2,))

        for index in make_indices(dims[:-1]):

            try:
                index = tuple(index)
            except TypeError:
                pass

            # Sort trace
            sx = np.sort(tx[index])

            # Append to list
            intervals[index] = calc_min_interval(sx, alpha)

        # Transpose back before returning
        return np.array(intervals)

    else:
        # Sort univariate node
        sx = np.sort(x)

        return np.array(calc_min_interval(sx, alpha))

@statfunc
def mc_error(x, batches=5):
    """
    Calculates the simulation standard error, accounting for non-independent
    samples. The trace is divided into batches, and the standard deviation of
    the batch means is calculated.

    :Arguments:
      x : Numpy array
          An array containing MCMC samples
      batches : integer
          Number of batchas
    """

    if x.ndim > 1:

        dims = np.shape(x)
        #ttrace = np.transpose(np.reshape(trace, (dims[0], sum(dims[1:]))))
        trace = np.transpose([t.ravel() for t in x])

        return np.reshape([mc_error(t, batches) for t in trace], dims[1:])

    else:
        if batches == 1: return np.std(x)/np.sqrt(len(x))

        try:
            batched_traces = np.resize(x, (batches, int(len(x)/batches)))
        except ValueError:
            # If batches do not divide evenly, trim excess samples
            resid = len(x) % batches
            new_shape = (batches, (len(x) - resid) / batches)
            batched_traces = np.resize(x[:-resid], new_shape)

        means = np.mean(batched_traces, 1)

        return np.std(means)/np.sqrt(batches)

@statfunc
def quantiles(x, qlist=(2.5, 25, 50, 75, 97.5)):
    """Returns a dictionary of requested quantiles from array

    :Arguments:
      x : Numpy array
          An array containing MCMC samples
      qlist : tuple or list
          A list of desired quantiles (defaults to (2.5, 25, 50, 75, 97.5))

    """

    # Make a copy of trace
    x = x.copy()

    # For multivariate node
    if x.ndim > 1:
        # Transpose first, then sort, then transpose back
        sx = np.sort(x.T).T
    else:
        # Sort univariate node
        sx = np.sort(x)

    try:
        # Generate specified quantiles
        quants = [sx[int(len(sx)*q/100.0)] for q in qlist]

        return dict(zip(qlist, quants))

    except IndexError:
        print("Too few elements for quantile calculation")


def df_summary(trace, varnames=None, stat_funcs=None, extend=False,
               alpha=0.05, batches=100):
    """Create a data frame with summary statistics.

    Parameters
    ----------
    trace : MultiTrace instance
    varnames : list
        Names of variables to include in summary
    stat_funcs : None or list
        A list of functions used to calculate statistics. By default,
        the mean, standard deviation, simulation standard error, and
        highest posterior density intervals are included.

        The functions will be given one argument, the samples for a
        variable as a 2 dimensional array, where the first axis
        corresponds to sampling iterations and the second axis
        represents the flattened variable (e.g., x__0, x__1,...). Each
        function should return either
        1) A `pandas.Series` instance containing the result of
           calculating the statistic along the first axis. The name
           attribute will be taken as the name of the statistic.
        2) A `pandas.DataFrame` where each column contains the
           result of calculating the statistic along the first axis.
           The column names will be taken as the names of the
           statistics.
    extend : boolean
        If True, use the statistics returned by `stat_funcs` in
        addition to, rather than in place of, the default statistics.
        This is only meaningful when `stat_funcs` is not None.
    alpha : float
        The alpha level for generating posterior intervals. Defaults
        to 0.05. This is only meaningful when `stat_funcs` is None.
    batches : int
        Batch size for calculating standard deviation for
        non-independent samples. Defaults to 100. This is only
        meaningful when `stat_funcs` is None.


    See also
    --------
    summary : Generate a pretty-printed summary of a trace.


    Returns
    -------
    `pandas.DataFrame` with summary statistics for each variable


    Examples
    --------

    >>> import pymc3 as pm
    >>> trace.mu.shape
    (1000, 2)
    >>> pm.df_summary(trace, ['mu'])
               mean        sd  mc_error     hpd_5    hpd_95
    mu__0  0.106897  0.066473  0.001818 -0.020612  0.231626
    mu__1 -0.046597  0.067513  0.002048 -0.174753  0.081924

    Other statistics can be calculated by passing a list of functions.

    >>> import pandas as pd
    >>> def trace_sd(x):
    ...     return pd.Series(np.std(x, 0), name='sd')
    ...
    >>> def trace_quantiles(x):
    ...     return pd.DataFrame(pm.quantiles(x, [5, 50, 95]))
    ...
    >>> pm.df_summary(trace, ['mu'], stat_funcs=[trace_sd, trace_quantiles])
                 sd         5        50        95
    mu__0  0.066473  0.000312  0.105039  0.214242
    mu__1  0.067513 -0.159097 -0.045637  0.062912
    """
    if varnames is None:
        varnames = trace.original_varnames

    funcs = [lambda x: pd.Series(np.mean(x, 0), name='mean'),
             lambda x: pd.Series(np.std(x, 0), name='sd'),
             lambda x: pd.Series(mc_error(x, batches), name='mc_error'),
             lambda x: _hpd_df(x, alpha)]

    if stat_funcs is not None and extend:
        stat_funcs = funcs + stat_funcs
    elif stat_funcs is None:
        stat_funcs = funcs

    var_dfs = []
    for var in varnames:
        vals = trace.get_values(var, combine=True)
        flat_vals = vals.reshape(vals.shape[0], -1)
        var_df = pd.concat([f(flat_vals) for f in stat_funcs], axis=1)
        var_df.index = ttab.create_flat_names(var, vals.shape[1:])
        var_dfs.append(var_df)
    return pd.concat(var_dfs, axis=0)


def _hpd_df(x, alpha):
    cnames = ['hpd_{0:g}'.format(100 * alpha/2),
              'hpd_{0:g}'.format(100 * (1 - alpha/2))]
    return pd.DataFrame(hpd(x, alpha), columns=cnames)


def summary(trace, varnames=None, alpha=0.05, start=0, batches=100, roundto=3,
            to_file=None):
    """
    Generate a pretty-printed summary of the node.

    :Parameters:
    trace : Trace object
      Trace containing MCMC sample

    varnames : list of strings
      List of variables to summarize. Defaults to None, which results
      in all variables summarized.

    alpha : float
      The alpha level for generating posterior intervals. Defaults to
      0.05.

    start : int
      The starting index from which to summarize (each) chain. Defaults
      to zero.

    batches : int
      Batch size for calculating standard deviation for non-independent
      samples. Defaults to 100.

    roundto : int
      The number of digits to round posterior statistics.

    tofile : None or string
      File to write results to. If not given, print to stdout.

    """
    if varnames is None:
        varnames = trace.original_varnames

    stat_summ = _StatSummary(roundto, batches, alpha)
    pq_summ = _PosteriorQuantileSummary(roundto, alpha)

    if to_file is None:
        fh = sys.stdout
    else:
        fh = open(to_file, mode='w')

    for var in varnames:
        # Extract sampled values
        sample = trace.get_values(var, burn=start, combine=True)

        fh.write('\n%s:\n\n' % var)

        fh.write(stat_summ.output(sample))
        fh.write(pq_summ.output(sample))

    if fh is not sys.stdout:
        fh.close()

class _Summary(object):
    """Base class for summary output"""
    def __init__(self, roundto):
        self.roundto = roundto
        self.header_lines = None
        self.leader = '  '
        self.spaces = None
        self.width = None

    def output(self, sample):
        return '\n'.join(list(self._get_lines(sample))) + '\n\n'

    def _get_lines(self, sample):
        for line in self.header_lines:
            yield self.leader + line
        summary_lines = self._calculate_values(sample)
        for line in self._create_value_output(summary_lines):
            yield self.leader + line

    def _create_value_output(self, lines):
        for values in lines:
            try:
                self._format_values(values)
                yield self.value_line.format(pad=self.spaces, **values).strip()
            except AttributeError:
            # This is a key for the leading indices, not a normal row.
            # `values` will be an empty tuple unless it is 2d or above.
                if values:
                    leading_idxs = [str(v) for v in values]
                    numpy_idx = '[{}, :]'.format(', '.join(leading_idxs))
                    yield self._create_idx_row(numpy_idx)
                else:
                    yield ''

    def _calculate_values(self, sample):
        raise NotImplementedError

    def _format_values(self, summary_values):
        for key, val in summary_values.items():
            summary_values[key] = '{:.{ndec}f}'.format(
                float(val), ndec=self.roundto)

    def _create_idx_row(self, value):
        return '{:.^{}}'.format(value, self.width)


class _StatSummary(_Summary):
    def __init__(self, roundto, batches, alpha):
        super(_StatSummary, self).__init__(roundto)
        spaces = 17
        hpd_name = '{0:g}% HPD interval'.format(100 * (1 - alpha))
        value_line = '{mean:<{pad}}{sd:<{pad}}{mce:<{pad}}{hpd:<{pad}}'
        header = value_line.format(mean='Mean', sd='SD', mce='MC Error',
                                  hpd=hpd_name, pad=spaces).strip()
        self.width = len(header)
        hline = '-' * self.width

        self.header_lines = [header, hline]
        self.spaces = spaces
        self.value_line = value_line
        self.batches = batches
        self.alpha = alpha

    def _calculate_values(self, sample):
        return _calculate_stats(sample, self.batches, self.alpha)

    def _format_values(self, summary_values):
        roundto = self.roundto
        for key, val in summary_values.items():
            if key == 'hpd':
                summary_values[key] = '[{:.{ndec}f}, {:.{ndec}f}]'.format(
                    *val, ndec=roundto)
            else:
                summary_values[key] = '{:.{ndec}f}'.format(
                    float(val), ndec=roundto)


class _PosteriorQuantileSummary(_Summary):
    def __init__(self, roundto, alpha):
        super(_PosteriorQuantileSummary, self).__init__(roundto)
        spaces = 15
        title = 'Posterior quantiles:'
        value_line = '{lo:<{pad}}{q25:<{pad}}{q50:<{pad}}{q75:<{pad}}{hi:<{pad}}'
        lo, hi = 100 * alpha / 2, 100 * (1. - alpha / 2)
        qlist = (lo, 25, 50, 75, hi)
        header = value_line.format(lo=lo, q25=25, q50=50, q75=75, hi=hi,
                                   pad=spaces).strip()
        self.width = len(header)
        hline = '|{thin}|{thick}|{thick}|{thin}|'.format(
            thin='-' * (spaces - 1), thick='=' * (spaces - 1))

        self.header_lines = [title, header, hline]
        self.spaces = spaces
        self.lo, self.hi = lo, hi
        self.qlist = qlist
        self.value_line = value_line

    def _calculate_values(self, sample):
        return _calculate_posterior_quantiles(sample, self.qlist)


def _calculate_stats(sample, batches, alpha):
    means = sample.mean(0)
    sds = sample.std(0)
    mces = mc_error(sample, batches)
    intervals = hpd(sample, alpha)
    for key, idxs in _groupby_leading_idxs(sample.shape[1:]):
        yield key
        for idx in idxs:
            mean, sd, mce = [stat[idx] for stat in (means, sds, mces)]
            interval = intervals[idx].squeeze().tolist()
            yield {'mean': mean, 'sd': sd, 'mce': mce, 'hpd': interval}


def _calculate_posterior_quantiles(sample, qlist):
    var_quantiles = quantiles(sample, qlist=qlist)
    ## Replace ends of qlist with 'lo' and 'hi'
    qends = {qlist[0]: 'lo', qlist[-1]: 'hi'}
    qkeys = {q: qends[q] if q in qends else 'q{}'.format(q) for q in qlist}
    for key, idxs in _groupby_leading_idxs(sample.shape[1:]):
        yield key
        for idx in idxs:
            yield {qkeys[q]: var_quantiles[q][idx] for q in qlist}


def _groupby_leading_idxs(shape):
    """Group the indices for `shape` by the leading indices of `shape`.

    All dimensions except for the rightmost dimension are used to create
    groups.

    A 3d shape will be grouped by the indices for the two leading
    dimensions.

        >>> for key, idxs in _groupby_leading_idxs((3, 2, 2)):
        ...     print('key: {}'.format(key))
        ...     print(list(idxs))
        key: (0, 0)
        [(0, 0, 0), (0, 0, 1)]
        key: (0, 1)
        [(0, 1, 0), (0, 1, 1)]
        key: (1, 0)
        [(1, 0, 0), (1, 0, 1)]
        key: (1, 1)
        [(1, 1, 0), (1, 1, 1)]
        key: (2, 0)
        [(2, 0, 0), (2, 0, 1)]
        key: (2, 1)
        [(2, 1, 0), (2, 1, 1)]

    A 1d shape will only have one group.

        >>> for key, idxs in _groupby_leading_idxs((2,)):
        ...     print('key: {}'.format(key))
        ...     print(list(idxs))
        key: ()
        [(0,), (1,)]
    """
    idxs = itertools.product(*[range(s) for s in shape])
    return itertools.groupby(idxs, lambda x: x[:-1])
