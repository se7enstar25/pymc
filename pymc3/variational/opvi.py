R"""
Variational inference is a great approach for doing really complex,
often intractable Bayesian inference in approximate form. Common methods
(e.g. ADVI) lack from complexity so that approximate posterior does not
reveal the true nature of underlying problem. In some applications it can
yield unreliable decisions.

Recently on NIPS 2017 `OPVI  <https://arxiv.org/abs/1610.09033/>`_ framework
was presented. It generalizes variational inverence so that the problem is
build with blocks. The first and essential block is Model itself. Second is
Approximation, in some cases :math:`log Q(D)` is not really needed. Necessity
depends on the third and forth part of that black box, Operator and
Test Function respectively.

Operator is like an approach we use, it constructs loss from given Model,
Approximation and Test Function. The last one is not needed if we minimize
KL Divergence from Q to posterior. As a drawback we need to compute :math:`loq Q(D)`.
Sometimes approximation family is intractable and :math:`loq Q(D)` is not available,
here comes LS(Langevin Stein) Operator with a set of test functions.

Test Function has more unintuitive meaning. It is usually used with LS operator
and represents all we want from our approximate distribution. For any given vector
based function of :math:`z` LS operator yields zero mean function under posterior.
:math:`loq Q(D)` is no more needed. That opens a door to rich approximation
families as neural networks.

References
----------
-   Rajesh Ranganath, Jaan Altosaar, Dustin Tran, David M. Blei
    Operator Variational Inference
    https://arxiv.org/abs/1610.09033 (2016)
"""

import warnings
import itertools
import numpy as np
import theano
import theano.tensor as tt
import pymc3 as pm
from .updates import adagrad_window
from ..distributions.dist_math import rho2sd, log_normal
from ..model import modelcontext
from ..blocking import (
    ArrayOrdering, DictToArrayBijection, VarMap
)
from ..util import get_default_varnames
from ..theanof import tt_rng, memoize, change_flags, identity


__all__ = [
    'ObjectiveFunction',
    'Operator',
    'TestFunction',
    'Approximation'
]


def node_property(f):
    """
    A shortcut for wrapping method to accessible tensor
    """
    return property(memoize(change_flags(compute_test_value='off')(f)))


@change_flags(compute_test_value='raise')
def try_to_set_test_value(node_in, node_out, s):
    _s = s
    if s is None:
        s = 1
    s = theano.compile.view_op(tt.as_tensor(s))
    if not isinstance(node_in, (list, tuple)):
        node_in = [node_in]
    if not isinstance(node_out, (list, tuple)):
        node_out = [node_out]
    for i, o in zip(node_in, node_out):
        if hasattr(i.tag, 'test_value'):
            if not hasattr(s.tag, 'test_value'):
                continue
            else:
                tv = i.tag.test_value[None, ...]
                tv = np.repeat(tv, s.tag.test_value, 0)
                if _s is None:
                    tv = tv[0]
                o.tag.test_value = tv


def get_transformed(z):
    if hasattr(z, 'transformed'):
        z = z.transformed
    return z


class ObjectiveUpdates(theano.OrderedUpdates):
    """
    OrderedUpdates extension for storing loss
    """
    loss = None


def _warn_not_used(smth, where):
    warnings.warn('`%s` is not used for %s and ignored' % (smth, where))


class ObjectiveFunction(object):
    """Helper class for construction loss and updates for variational inference

    Parameters
    ----------
    op : :class:`Operator`
        OPVI Functional operator
    tf : :class:`TestFunction`
        OPVI TestFunction
    """

    def __init__(self, op, tf):
        self.op = op
        self.tf = tf

    obj_params = property(lambda self: self.op.approx.params)
    test_params = property(lambda self: self.tf.params)
    approx = property(lambda self: self.op.approx)

    def updates(self, obj_n_mc=None, tf_n_mc=None, obj_optimizer=adagrad_window, test_optimizer=adagrad_window,
                more_obj_params=None, more_tf_params=None, more_updates=None,
                more_replacements=None, total_grad_norm_constraint=None):
        """Calculates gradients for objective function, test function and then
        constructs updates for optimization step

        Parameters
        ----------
        obj_n_mc : `int`
            Number of monte carlo samples used for approximation of objective gradients
        tf_n_mc : `int`
            Number of monte carlo samples used for approximation of test function gradients
        obj_optimizer : function (loss, params) -> updates
            Optimizer that is used for objective params
        test_optimizer : function (loss, params) -> updates
            Optimizer that is used for test function params
        more_obj_params : `list`
            Add custom params for objective optimizer
        more_tf_params : `list`
            Add custom params for test function optimizer
        more_updates : `dict`
            Add custom updates to resulting updates
        more_replacements : `dict`
            Apply custom replacements before calculating gradients
        total_grad_norm_constraint : `float`
            Bounds gradient norm, prevents exploding gradient problem

        Returns
        -------
        :class:`ObjectiveUpdates`
        """
        if more_updates is None:
            more_updates = dict()
        resulting_updates = ObjectiveUpdates()
        if self.test_params:
            self.add_test_updates(
                resulting_updates,
                tf_n_mc=tf_n_mc,
                test_optimizer=test_optimizer,
                more_tf_params=more_tf_params,
                more_replacements=more_replacements,
                total_grad_norm_constraint=total_grad_norm_constraint
            )
        else:
            if tf_n_mc is not None:
                _warn_not_used('tf_n_mc', self.op)
            if more_tf_params:
                _warn_not_used('more_tf_params', self.op)
        self.add_obj_updates(
            resulting_updates,
            obj_n_mc=obj_n_mc,
            obj_optimizer=obj_optimizer,
            more_obj_params=more_obj_params,
            more_replacements=more_replacements,
            total_grad_norm_constraint=total_grad_norm_constraint
        )
        resulting_updates.update(more_updates)
        return resulting_updates

    def add_test_updates(self, updates, tf_n_mc=None, test_optimizer=adagrad_window,
                         more_tf_params=None, more_replacements=None,
                         total_grad_norm_constraint=None):
        if more_tf_params is None:
            more_tf_params = []
        if more_replacements is None:
            more_replacements = dict()
        tf_target = self(tf_n_mc, more_tf_params=more_tf_params)
        tf_target = theano.clone(tf_target, more_replacements, strict=False)
        grads = pm.updates.get_or_compute_grads(tf_target, self.obj_params + more_tf_params)
        if total_grad_norm_constraint is not None:
            grads = pm.total_norm_constraint(grads, total_grad_norm_constraint)
        updates.update(
            test_optimizer(
                grads,
                self.test_params +
                more_tf_params))

    def add_obj_updates(self, updates, obj_n_mc=None, obj_optimizer=adagrad_window,
                        more_obj_params=None, more_replacements=None,
                        total_grad_norm_constraint=None):
        if more_obj_params is None:
            more_obj_params = []
        if more_replacements is None:
            more_replacements = dict()
        obj_target = self(obj_n_mc, more_obj_params=more_obj_params)
        obj_target = theano.clone(obj_target, more_replacements, strict=False)
        grads = pm.updates.get_or_compute_grads(obj_target, self.obj_params + more_obj_params)
        if total_grad_norm_constraint is not None:
            grads = pm.total_norm_constraint(grads, total_grad_norm_constraint)
        updates.update(
            obj_optimizer(
                grads,
                self.obj_params +
                more_obj_params))
        if self.op.RETURNS_LOSS:
            updates.loss = obj_target

    @memoize
    @change_flags(compute_test_value='off')
    def step_function(self, obj_n_mc=None, tf_n_mc=None,
                      obj_optimizer=adagrad_window, test_optimizer=adagrad_window,
                      more_obj_params=None, more_tf_params=None,
                      more_updates=None, more_replacements=None,
                      total_grad_norm_constraint=None,
                      score=False, fn_kwargs=None):
        R"""Step function that should be called on each optimization step.

        Generally it solves the following problem:

        .. math::

                \mathbf{\lambda^{*}} = \inf_{\lambda} \sup_{\theta} t(\mathbb{E}_{\lambda}[(O^{p,q}f_{\theta})(z)])

        Parameters
        ----------
        obj_n_mc : `int`
            Number of monte carlo samples used for approximation of objective gradients
        tf_n_mc : `int`
            Number of monte carlo samples used for approximation of test function gradients
        obj_optimizer : function (loss, params) -> updates
            Optimizer that is used for objective params
        test_optimizer : function (loss, params) -> updates
            Optimizer that is used for test function params
        more_obj_params : `list`
            Add custom params for objective optimizer
        more_tf_params : `list`
            Add custom params for test function optimizer
        more_updates : `dict`
            Add custom updates to resulting updates
        total_grad_norm_constraint : `float`
            Bounds gradient norm, prevents exploding gradient problem
        score : `bool`
            calculate loss on each step? Defaults to False for speed
        fn_kwargs : `dict`
            Add kwargs to theano.function (e.g. `{'profile': True}`)
        more_replacements : `dict`
            Apply custom replacements before calculating gradients

        Returns
        -------
        `theano.function`
        """
        if fn_kwargs is None:
            fn_kwargs = {}
        if score and not self.op.RETURNS_LOSS:
            raise NotImplementedError('%s does not have loss' % self.op)
        updates = self.updates(obj_n_mc=obj_n_mc, tf_n_mc=tf_n_mc,
                               obj_optimizer=obj_optimizer,
                               test_optimizer=test_optimizer,
                               more_obj_params=more_obj_params,
                               more_tf_params=more_tf_params,
                               more_updates=more_updates,
                               more_replacements=more_replacements,
                               total_grad_norm_constraint=total_grad_norm_constraint)
        if score:
            step_fn = theano.function(
                [], updates.loss, updates=updates, **fn_kwargs)
        else:
            step_fn = theano.function([], None, updates=updates, **fn_kwargs)
        return step_fn

    @memoize
    @change_flags(compute_test_value='off')
    def score_function(self, sc_n_mc=None, more_replacements=None, fn_kwargs=None):   # pragma: no cover
        R"""Compiles scoring function that operates which takes no inputs and returns Loss

        Parameters
        ----------
        sc_n_mc : `int`
            number of scoring MC samples
        more_replacements:
            Apply custom replacements before compiling a function
        fn_kwargs: `dict`
            arbitrary kwargs passed to theano.function

        Returns
        -------
        theano.function
        """
        if fn_kwargs is None:
            fn_kwargs = {}
        if not self.op.RETURNS_LOSS:
            raise NotImplementedError('%s does not have loss' % self.op)
        if more_replacements is None:
            more_replacements = {}
        loss = theano.clone(
            self(sc_n_mc),
            more_replacements,
            strict=False)
        return theano.function([], loss, **fn_kwargs)

    def __getstate__(self):
        return self.op, self.tf

    def __setstate__(self, state):
        self.__init__(*state)

    @change_flags(compute_test_value='off')
    def __call__(self, nmc, **kwargs):
        if 'more_tf_params' in kwargs:
            m = -1.
        else:
            m = 1.
        a = self.op.apply(self.tf)
        a = self.approx.set_size_and_deterministic(a, nmc, 0)
        return m * self.op.T(a)


class Operator(object):
    R"""Base class for Operator

    Parameters
    ----------
    approx : :class:`Approximation`
        an approximation instance

    Notes
    -----
    For implementing Custom operator it is needed to define :func:`Operator.apply` method
    """

    HAS_TEST_FUNCTION = False
    RETURNS_LOSS = True
    SUPPORT_AEVB = True
    OBJECTIVE = ObjectiveFunction
    T = identity

    def __init__(self, approx):
        if not self.SUPPORT_AEVB and approx.local_vars:
            raise ValueError('%s does not support AEVB, '
                             'please change inference method' % type(self))
        self.model = approx.model
        self.approx = approx

    flat_view = property(lambda self: self.approx.flat_view)
    input = property(lambda self: self.approx.flat_view.input)

    logp = property(lambda self: self.approx.logp)
    logq = property(lambda self: self.approx.logq)
    logp_norm = property(lambda self: self.approx.logp_norm)
    logq_norm = property(lambda self: self.approx.logq_norm)

    def apply(self, f):   # pragma: no cover
        R"""Operator itself

        .. math::

            (O^{p,q}f_{\theta})(z)

        Parameters
        ----------
        f : :class:`TestFunction` or None
            function that takes `z = self.input` and returns
            same dimensional output

        Returns
        -------
        `TensorVariable`
            symbolically applied operator
        """
        raise NotImplementedError

    def __call__(self, f=None):
        if self.HAS_TEST_FUNCTION:
            if f is None:
                raise ValueError('Operator %s requires TestFunction' % self)
            else:
                if not isinstance(f, TestFunction):
                    f = TestFunction.from_function(f)
        else:
            if f is not None:
                warnings.warn(
                    'TestFunction for %s is redundant and removed' %
                    self)
            else:
                pass
            f = TestFunction()
        f.setup(self.approx.total_size)
        return self.OBJECTIVE(self, f)

    def __getstate__(self):
        # pickle only important parts
        return self.approx

    def __setstate__(self, approx):
        self.__init__(approx)

    def __str__(self):    # pragma: no cover
        return '%(op)s[%(ap)s]' % dict(op=self.__class__.__name__,
                                       ap=self.approx.__class__.__name__)


def collect_shared_to_list(params):
    """Helper function for getting a list from
    usable representation of parameters

    Parameters
    ----------
    params : {dict|None}

    Returns
    -------
    list
    """
    if isinstance(params, dict):
        return list(
            t[1] for t in sorted(params.items(), key=lambda t: t[0])
            if isinstance(t[1], theano.compile.SharedVariable)
        )
    elif params is None:
        return []
    else:
        raise TypeError(
            'Unknown type %s for %r, need dict or None')


class TestFunction(object):
    def __init__(self):
        self._inited = False
        self.shared_params = None

    def create_shared_params(self, dim):
        """Returns
        -------
        {dict|list|theano.shared}
        """
        pass

    @property
    def params(self):
        return collect_shared_to_list(self.shared_params)

    def __call__(self, z):
        raise NotImplementedError

    def setup(self, dim):
        if not self._inited:
            self._setup(dim)
            self.shared_params = self.create_shared_params(dim)
            self._inited = True

    def _setup(self, dim):
        R"""Does some preparation stuff before calling :func:`Approximation.create_shared_params`

        Parameters
        ----------
        dim : int
            dimension of posterior distribution
        """
        pass

    @classmethod
    def from_function(cls, f):
        if not callable(f):
            raise ValueError('Need callable, got %r' % f)
        obj = TestFunction()
        obj.__call__ = f
        return obj


class Group(object):
    """
    Grouped Approximation that is used for modelling mutual dependencies
    for a specified group of variables. Base for local and global group
    """
    # need to be defined in init
    shared_params = None
    symbolic_initial = None
    replacements = None
    input = None

    # defined by approximation
    SUPPORT_AEVB = True
    initial_dist_name = 'normal'
    initial_dist_map = 0.

    def __new__(cls, *args, **kwargs):
        # dynamic dispatching
        is_local = kwargs.get('local', False)
        if is_local:
            _cls = Local
        else:
            _cls = Global
        return object.__new__(_cls)

    def __init__(self, group=None,
                 params=None,
                 random_seed=None,
                 model=None,
                 local=False):
        self._is_local = local
        self._rng = tt_rng(random_seed)
        model = modelcontext(model)
        self.model = model
        if group is None:
            self.group = model.vars
        elif group is -1:  # ints have unique pointer
            self.group = -1
        else:
            self.group = group
        if params is None:
            params = dict()
        self.user_params = params
        self.vmap = dict()
        self.ndim = 0
        if self.group is not -1:
            # init can be delayed
            self.__init_group__(self.group)

    def __init_group__(self, group):
        if not group:
            raise ValueError('Got empty group')
        if self.group is -1:
            # delayed init
            self.group = group

    @property
    def is_local(self):
        return self.is_local

    @property
    def params_dict(self):
        if self.user_params is not None:
            return self.user_params
        else:
            return self.shared_params

    @property
    def params(self):
        return collect_shared_to_list(self.params_dict)

    def to_flat_input(self, node):
        """
        Replaces vars with flattened view stored in self.input
        """
        return theano.clone(node, self.replacements, strict=False)

    def _new_initial_shape(self, size, ndim):
        raise NotImplementedError

    def _new_initial_(self, size, deterministic):
        if size is None:
            size = 1
        if not isinstance(deterministic, tt.Variable):
            deterministic = np.int8(deterministic)
        ndim, dist_name, dist_map = (
            self.ndim,
            self.initial_dist_name,
            self.initial_dist_map
        )
        dtype = self.symbolic_initial.dtype
        ndim = tt.as_tensor(ndim)
        size = tt.as_tensor(size)
        shape = self._new_initial_shape(size, ndim)
        # apply optimizations if possible
        if not isinstance(deterministic, tt.Variable):
            if deterministic:
                return tt.ones(shape, dtype) * dist_map
            else:
                return getattr(self._rng, dist_name)(shape)
        else:
            sample = getattr(self._rng, dist_name)(shape)
            initial = tt.switch(
                deterministic,
                tt.ones(shape, dtype) * dist_map,
                sample
            )
            return initial

    @node_property
    def symbolic_random(self):
        raise NotImplementedError

    @change_flags(compute_test_value='off')
    def set_size_and_deterministic(self, node, s, d):
        initial_ = self._new_initial_(s, d)
        # optimizations
        out = theano.clone(node, {
            self.symbolic_initial: initial_,
        })
        try_to_set_test_value(node, out, None)
        return out

    @node_property
    def symbolic_normalizing_constant(self):
        """
        Constant to divide when we want to scale down loss from minibatches
        """
        t = self.to_flat_input(
            tt.max([v.scaling for v in self.group]))
        t = theano.clone(t, {
            self.input: self.symbolic_random[0]
        })
        t = self.set_size_and_deterministic(t, 1, 1)  # remove random, we do not it here at all
        return pm.floatX(t)

    @node_property
    def symbolic_logq(self):
        raise NotImplementedError  # shape (s,)

    @node_property
    def logq(self):
        return self.symbolic_logq.mean(0)

    @node_property
    def logq_norm(self):
        return self.logq / self.symbolic_normalizing_constant

    def _get_batch_size(self):
        raise NotImplementedError


class Global(Group):
    """
    Base class for global variables
    """
    @change_flags(compute_test_value='off')
    def __init_group__(self, group):
        super(Global, self).__init_group__(group)
        self.symbolic_initial = tt.matrix(self.__class__.__name__ + '_symbolic_initial_matrix')
        self.input = tt.vector(self.__class__.__name__ + '_symbolic_input')
        for var in group:
            var = get_transformed(var)
            begin = self.ndim
            self.ndim += var.dsize
            end = self.ndim
            self.vmap[var] = VarMap(var.name, slice(begin, end), var.dshape, var.dtype)
        self.replacements = dict()
        for v, (name, slc, shape, dtype) in self.vmap.items():
            # slice is taken only by last dimension
            vr = self.input[slc].reshape(shape).astype(dtype)
            vr.name = name + '_vi_replacement'
            self.replacements[v] = vr

    def _new_initial_shape(self, size, ndim):
        raise tt.stack([size, ndim])


class Local(Group):
    """
    Base class for local variables
    """
    @change_flags(compute_test_value='off')
    def __init_group__(self, group):
        super(Local, self).__init_group__(group)
        if len(group) > 1:
            raise TypeError('Local groups with more than 1 variable are not supported')
        self.symbolic_initial = tt.tensor3(self.__class__.__name__ + '_symbolic_initial_tensor')
        self.input = tt.matrix(self.__class__.__name__ + '_symbolic_input')
        for var in group:
            var = get_transformed(var)
            begin = self.ndim
            self.ndim += np.prod(var.dshape[1:])
            end = self.ndim
            shape = (-1, ) + var.dshape[1:]
            self.vmap[var] = VarMap(var.name, slice(begin, end), shape, var.dtype)
        self.replacements = dict()
        for v, (name, slc, shape, dtype) in self.vmap.items():
            # slice is taken only by last dimension
            vr = self.input[..., slc].reshape(shape).astype(dtype)
            vr.name = name + '_vi_replacement'
            self.replacements[v] = vr

    def _new_initial_shape(self, size, ndim):
        raise tt.stack([size, self._get_batch_size(), ndim])


class GroupedApproximation(object):
    def __init__(self, groups, model=None):
        model = modelcontext(model)
        seen = set()
        rest = None
        for g in groups:
            if g.group is -1:
                if rest is not None:
                    raise TypeError('More that one group is specified for '
                                    'the rest variables')
                else:
                    rest = g
            if set(g.group) & seen:
                raise ValueError('Found duplicates in groups')
            seen.update(g.group)
        if set(model.free_RVs) - seen:
            if rest is None:
                raise ValueError('No approximation is specified for the rest variables')
            else:
                rest.__init_group__(set(model.free_RVs) - seen)
        self.groups = groups
        self.model = model

    def _collect(self, item):
        return [getattr(g, item) for g in self.groups]

    inputs = property(lambda self: self._collect('input'))
    symbolic_randoms = property(lambda self: self._collect('symbolic_random'))

    @node_property
    def symbolic_normalizing_constant(self):
        return tt.max(self._collect('symbolic_normalizing_constant'))

    @node_property
    def symbolic_logq(self):
        return tt.add(*self._collect('symbolic_logq'))

    @node_property
    def logq(self):
        return self.symbolic_logq.mean(0)

    @node_property
    def sized_symbolic_logp(self):
        logp = self.to_flat_input(self.model.logpt)
        free_logp_local = self.sample_over_posterior(logp)
        return free_logp_local  # shape (s,)

    @node_property
    def logp(self):
        return self.sized_symbolic_logp.mean(0)

    @node_property
    def single_symbolic_logp(self):
        logp = self.to_flat_input(self.model.logpt)
        post = [v[0] for v in self.symbolic_randoms]
        inp = self.inputs
        return theano.clone(
            logp, dict(zip(inp, post))
        )

    @property
    def replacements(self):
        return dict(itertools.chain(
            *[g.replacements.items()
              for g in self.groups]
        ))

    def construct_replacements(self, more_replacements=None):
        replacements = self.replacements
        if more_replacements is not None:
            replacements.update(more_replacements)
        return more_replacements

    @change_flags(compute_test_value='off')
    def set_size_and_deterministic(self, node, s, d):
        optimizations = self._get_optimization_replacements(s, d)
        node = theano.clone(node, optimizations)
        for g in self.groups:
            node = g.set_size_and_deterministic(node, s, d)
        return node

    def to_flat_input(self, node):
        """
        Replaces vars with flattened view stored in self.inputs
        """
        return theano.clone(node, self.replacements, strict=False)

    def sample_over_posterior(self, node):
        node = self.to_flat_input(node)

        def sample(*post):
            return theano.clone(node, dict(zip(self.inputs, post)))

        nodes, _ = theano.scan(
            sample, self.symbolic_randoms)
        return nodes

    def _get_optimization_replacements(self, s, d):
        repl = dict()
        if isinstance(s, int) and (s == 1) or s is None:
            repl[self.logp] = self.single_symbolic_logp
        return repl

    @change_flags(compute_test_value='off')
    def sample_node(self, node, size=100,
                    deterministic=False,
                    more_replacements=None):
        """Samples given node or nodes over shared posterior

        Parameters
        ----------
        node : Theano Variables (or Theano expressions)
        size : None or scalar
            number of samples
        more_replacements : `dict`
            add custom replacements to graph, e.g. change input source
        deterministic : bool
            whether to use zeros as initial distribution
            if True - zero initial point will produce constant latent variables

        Returns
        -------
        sampled node(s) with replacements
        """
        node_in = node
        node = theano.clone(node, more_replacements)
        if size is None:
            node_out = self.to_flat_input(node)
            node_out = theano.clone(node_out, self.replacements)
        else:
            node_out = self.sample_over_posterior(node)
        node_out = self.set_size_and_deterministic(node_out, size, deterministic)
        try_to_set_test_value(node_in, node_out, size)
        return node_out

    @property
    @memoize
    @change_flags(compute_test_value='off')
    def sample_dict_fn(self):
        s = tt.iscalar()
        flat_inp_vars = self.to_flat_input(self.model.free_RVs)
        sampled = self.sample_over_posterior(flat_inp_vars)
        sampled = self.set_size_and_deterministic(sampled, s, 0)
        sample_fn = theano.function([s], sampled)

        def inner(draws=100):
            _samples = sample_fn(draws)
            return dict([(v_.name, s_) for v_, s_ in zip(self.model.free_RVs, _samples)])

        return inner

    def sample(self, draws=500, include_transformed=True):
        """Draw samples from variational posterior.

        Parameters
        ----------
        draws : `int`
            Number of random samples.
        include_transformed : `bool`
            If True, transformed variables are also sampled. Default is False.

        Returns
        -------
        trace : :class:`pymc3.backends.base.MultiTrace`
            Samples drawn from variational posterior.
        """
        vars_sampled = get_default_varnames(self.model.unobserved_RVs,
                                            include_transformed=include_transformed)
        samples = self.sample_dict_fn(draws)  # type: dict
        trace = pm.sampling.NDArray(model=self.model, vars=vars_sampled)
        points = ({name: samples[name][i] for name in samples.keys()} for i in range(draws))
        try:
            trace.setup(draws=draws, chain=0)
            for point in points:
                trace.record(point)
        finally:
            trace.close()
        return pm.sampling.MultiTrace([trace])
