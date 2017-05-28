import collections

import numpy as np

__all__ = [
    'Callback',
    'CheckParametersConvergence',
    'Tracker'
]


class Callback(object):
    def __call__(self, approx, loss, i):
        raise NotImplementedError


def relative(current, prev, eps=1e-6):
    return (np.abs(current - prev) + eps) / (np.abs(prev) + eps)


def absolute(current, prev):
    return np.abs(current - prev)


_diff = dict(
    relative=relative,
    absolute=absolute
)


class CheckParametersConvergence(Callback):
    """Convergence stopping check

    Parameters
    ----------
    every : int
        check frequency
    tolerance : float
        if diff norm < tolerance : break
    diff : str
        difference type one of {'absolute', 'relative'}
    ord : {non-zero int, inf, -inf, 'fro', 'nuc'}, optional
        see more info in :func:`numpy.linalg.norm`

    Examples
    --------
    >>> with model:
    ...     approx = pm.fit(
    ...         n=10000, callbacks=[
    ...             CheckParametersConvergence(
    ...                 every=50, diff='absolute',
    ...                 tolerance=1e-4)
    ...         ]
    ...     )
    """

    def __init__(self, every=100, tolerance=1e-3,
                 diff='relative', ord=np.inf):
        self._diff = _diff[diff]
        self.ord = ord
        self.every = every
        self.prev = None
        self.tolerance = tolerance

    def __call__(self, approx, _, i):
        if self.prev is None:
            self.prev = self.flatten_shared(approx.params)
            return
        if i % self.every or i < self.every:
            return
        current = self.flatten_shared(approx.params)
        prev = self.prev
        delta = self._diff(current, prev)  # type: np.ndarray
        self.prev = current
        norm = np.linalg.norm(delta, self.ord)
        if norm < self.tolerance:
            raise StopIteration('Convergence archived at %d' % i)

    @staticmethod
    def flatten_shared(shared_list):
        return np.concatenate([sh.get_value().flatten() for sh in shared_list])


class Tracker(Callback):
    """
    Helper class to record arbitrary stats during VI

    It is possible to pass a function that takes no arguments
    If call fails then (approx, hist, i) are passed


    Parameters
    ----------
    kwargs : key word arguments
        keys mapping statname to callable that records the stat

    Examples
    --------
    Consider we want time on each iteration    
    >>> import time
    >>> tracker = Tracker(time=time.time)
    >>> with model:
    ...     approx = pm.fit(callbacks=[tracker])
    
    Time can be accessed via :code:`tracker['time']` now
    For more complex summary one can use callable that takes
    (approx, hist, i) as arguments
    >>> with model:
    ...     my_callable = lambda ap, h, i: h[-1]
    ...     tracker = Tracker(some_stat=my_callable)
    ...     approx = pm.fit(callbacks=[tracker])
    
    Multiple stats are valid too
    >>> with model:
    ...     tracker = Tracker(some_stat=my_callable, time=time.time)
    ...     approx = pm.fit(callbacks=[tracker])
    """
    def __init__(self, **kwargs):
        self.whatchdict = kwargs
        self.hist = collections.defaultdict(list)

    def record(self, approx, hist, i):
        for key, fn in self.whatchdict.items():
            try:
                res = fn()
            # if `*t` argument is used
            # fail will be somehow detected.
            # We want both calls to be tried.
            # Upper one has more priority as
            # arbitrary functions can have some
            # defaults in positionals. Bad idea
            # to try fn(approx, hist, i) first
            except Exception:
                res = fn(approx, hist, i)
            self.hist[key].append(res)

    def clear(self):
        self.hist = collections.defaultdict(list)

    def __getitem__(self, item):
        return self.hist[item]

    __call__ = record
