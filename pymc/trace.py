import numpy as np
from .core import *
from .stats import *
import copy
import types
import itertools

__all__ = ['summary']


# TODO: Move this to pymc.stats. (It was left here for diffing
# purposes).
def summary(trace, vars=None, alpha=0.05, start=0, batches=100, roundto=3):
    """
    Generate a pretty-printed summary of the node.

    :Parameters:
    trace : Trace object
      Trace containing MCMC sample

    vars : list of strings
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

    """
    if vars is None:
        vars = trace.varnames

    stat_summ = _StatSummary(roundto, batches, alpha)
    pq_summ = _PosteriorQuantileSummary(roundto, alpha)

    for var in vars:
        # Extract sampled values
        sample = trace.get_values(var, burn=start, combine=True)

        print('\n%s:' % var)
        print(' ')

        stat_summ.print_output(sample)
        pq_summ.print_output(sample)


class _Summary(object):
    """Base class for summary output"""
    def __init__(self, roundto):
        self.roundto = roundto
        self.header_lines = None
        self.leader = '  '
        self.spaces = None
        self.width = None

    def print_output(self, sample):
        print('\n'.join(list(self._get_lines(sample))) + '\n')

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
        hpd_name = '{}% HPD interval'.format(int(100 * (1 - alpha)))
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
