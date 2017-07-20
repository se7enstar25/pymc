from .compound import CompoundStep
from ..model import modelcontext
from ..theanof import inputvars
from ..blocking import ArrayOrdering, DictToArrayBijection
import numpy as np
from numpy.random import uniform
from enum import IntEnum, unique

__all__ = [
    'ArrayStep', 'ArrayStepShared', 'metrop_select', 'Competence']


@unique
class Competence(IntEnum):
    """Enum for charaterizing competence classes of step methods.
    Values include:
    0: INCOMPATIBLE
    1: COMPATIBLE
    2: PREFERRED
    3: IDEAL
    """
    INCOMPATIBLE = 0
    COMPATIBLE = 1
    PREFERRED = 2
    IDEAL = 3


class BlockedStep(object):

    generates_stats = False

    def __new__(cls, *args, **kwargs):
        blocked = kwargs.get('blocked')
        if blocked is None:
            # Try to look up default value from class
            blocked = getattr(cls, 'default_blocked', True)
            kwargs['blocked'] = blocked

        model = modelcontext(kwargs.get('model'))
        kwargs.update({'model':model})

        # vars can either be first arg or a kwarg
        if 'vars' not in kwargs and len(args) >= 1:
            vars = args[0]
            args = args[1:]
        elif 'vars' in kwargs:
            vars = kwargs.pop('vars')
        else:  # Assume all model variables
            vars = model.vars

        # get the actual inputs from the vars
        vars = inputvars(vars)

        if len(vars) == 0:
            raise ValueError('No free random variables to sample.')

        if not blocked and len(vars) > 1:
            # In this case we create a separate sampler for each var
            # and append them to a CompoundStep
            steps = []
            for var in vars:
                step = super(BlockedStep, cls).__new__(cls)
                # If we don't return the instance we have to manually
                # call __init__
                step.__init__([var], *args, **kwargs)
                # Hack for creating the class correctly when unpickling.
                step.__newargs = ([var], ) + args, kwargs
                steps.append(step)

            return CompoundStep(steps)
        else:
            step = super(BlockedStep, cls).__new__(cls)
            # Hack for creating the class correctly when unpickling.
            step.__newargs = (vars, ) + args, kwargs
            return step

    # Hack for creating the class correctly when unpickling.
    def __getnewargs_ex__(self):
        return self.__newargs

    @staticmethod
    def competence(var):
        return Competence.INCOMPATIBLE

    @classmethod
    def _competence(cls, vars):
        return [cls.competence(var) for var in np.atleast_1d(vars)]


class ArrayStep(BlockedStep):
    """
    Blocked step method that is generalized to accept vectors of variables.

    Parameters
    ----------
    vars : list
        List of variables for sampler.
    fs: list of logp theano functions
    allvars: Boolean (default False)
    blocked: Boolean (default True)
    """

    def __init__(self, vars, fs, allvars=False, blocked=True):
        self.vars = vars
        self.ordering = ArrayOrdering(vars)
        self.fs = fs
        self.allvars = allvars
        self.blocked = blocked

    def step(self, point):
        bij = DictToArrayBijection(self.ordering, point)

        inputs = [bij.mapf(x) for x in self.fs]
        if self.allvars:
            inputs.append(point)

        if self.generates_stats:
            apoint, stats = self.astep(bij.map(point), *inputs)
            return bij.rmap(apoint), stats
        else:
            apoint = self.astep(bij.map(point), *inputs)
            return bij.rmap(apoint)


class ArrayStepShared(BlockedStep):
    """Faster version of ArrayStep that requires the substep method that does not wrap
       the functions the step method uses.

    Works by setting shared variables before using the step. This eliminates the mapping
    and unmapping overhead as well as moving fewer variables around.
    """

    def __init__(self, vars, shared, blocked=True):
        """
        Parameters
        ----------
        vars : list of sampling variables
        shared : dict of theano variable -> shared variable
        blocked : Boolean (default True)
        """
        self.vars = vars
        self.ordering = ArrayOrdering(vars)
        self.shared = {str(var): shared for var, shared in shared.items()}
        self.blocked = blocked

    def step(self, point):
        for var, share in self.shared.items():
            share.set_value(point[var])

        bij = DictToArrayBijection(self.ordering, point)

        if self.generates_stats:
            apoint, stats = self.astep(bij.map(point))
            return bij.rmap(apoint), stats
        else:
            apoint = self.astep(bij.map(point))
            return bij.rmap(apoint)


class GradientSharedStep(BlockedStep):
    def __init__(self, vars, model=None, blocked=True,
                 dtype=None, **theano_kwargs):
        model = modelcontext(model)
        self.vars = vars
        self.blocked = blocked

        self._logp_dlogp_func = model.logp_dlogp_function(
            vars, dtype=dtype, **theano_kwargs)

    def step(self, point):
        self._logp_dlogp_func.set_extra_values(point)
        array = self._logp_dlogp_func.dict_to_array(point)

        if self.generates_stats:
            apoint, stats = self.astep(array)
            point = self._logp_dlogp_func.array_to_full_dict(apoint)
            return point, stats
        else:
            apoint = self.astep(array)
            point = self._logp_dlogp_func.array_to_full_dict(apoint)
            return point


def metrop_select(mr, q, q0):
    """Perform rejection/acceptance step for Metropolis class samplers.

    Returns the new sample q if a uniform random number is less than the
    metropolis acceptance rate (`mr`), and the old sample otherwise, along
    with a boolean indicating whether the sample was accepted.

    Parameters
    ----------
    mr : float, Metropolis acceptance rate
    q : proposed sample
    q0 : current sample

    Returns
    -------
    q or q0
    """
    # Compare acceptance ratio to uniform random number
    if np.isfinite(mr) and np.log(uniform()) < mr:
        return q, True
    else:
        return q0, False
