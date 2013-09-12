'''
Created on Mar 12, 2011

@author: johnsalvatier
'''
from scipy import optimize
import numpy as np
from numpy import isfinite, nan_to_num
from ..core import *

__all__ = ['find_MAP', 'scipyminimize']


def find_MAP(start=None, vars=None, fmin=optimize.fmin_bfgs, return_raw=False, disp=False, model=None, *args, **kwargs):
    """
    Sets state to the local maximum a posteriori point given a model.
    Current default of fmin_Hessian does not deal well with optimizing close
    to sharp edges, especially if they are the minimum.

    Parameters
    ----------
    start : dict of parameter values (Defaults to model.test_point)
    vars : list
        List of variables to set to MAP point (Defaults to all continuous).
    fmin : function
        Optimization algorithm (Defaults to `scipy.optimize.fmin_bfgs`).
    return_raw : Bool
        Whether to return extra value returned by fmin (Defaults to False)
    model : Model (optional if in `with` context)
    *args, **kwargs
        Extra args passed to fmin
    """
    model = modelcontext(model)
    if start is None:
        start = model.test_point

    if vars is None:
        vars = model.cont_vars

    allinmodel(vars, model)

    start = Point(start, model=model)
    bij = DictToArrayBijection(ArrayOrdering(vars), start)

    logp = bij.mapf(model.logpc)
    dlogp = bij.mapf(model.dlogpc(vars))

    def logp_o(point):
        return nan_to_high(-logp(point))

    def grad_logp_o(point):
        return nan_to_num(-dlogp(point))

    r = fmin(logp_o, bij.map(
        start), fprime=grad_logp_o, disp=disp, *args, **kwargs)
    if isinstance(r, tuple):
        mx = r[0]
    else:
        mx = r

    if (not allfinite(mx) or
        not allfinite(logp(mx)) or
            not allfinite(dlogp(mx))):
            raise ValueError("Optimization error: max, logp or dlogp at max have bad values. Some values may be outside of distribution support. max: " + repr(mx) + " logp: " + repr(logp(mx)) + " dlogp: " + repr(dlogp(mx)) +
                             "Check that 1) you don't have hierarchical parameters, these will lead to points with infinite density. 2) your distribution logp's are properly specified.")

    mx = bij.rmap(mx)
    if return_raw:
        return mx, r
    else:
        return mx


def allfinite(x):
    return np.all(isfinite(x))


def nan_to_high(x):
    return np.where(isfinite(x), x, 1.0e100)


def scipyminimize(f, x0, fprime, *args, **kwargs):
    r = scipy.optimize.minimize(f, x0, jac=fprime, *args, **kwargs)
    return r.x, r


def allinmodel(vars, model):
    notin = [v for v in vars if v not in model.vars]
    if notin:
        raise ValueError("Some variables not in the model: " + str(notin))
