#   Copyright 2020 The PyMC Developers
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from collections import OrderedDict

import numpy as np
from scipy.special import logsumexp
from theano import function as theano_function

from ..model import modelcontext, Point
from ..theanof import floatX, inputvars, make_shared_replacements, join_nonshared_inputs
from ..sampling import sample_prior_predictive
from ..backends.ndarray import NDArray


class SMC:
    def __init__(
        self,
        draws=2000,
        kernel="metropolis",
        n_steps=25,
        start=None,
        tune_steps=True,
        p_acc_rate=0.99,
        threshold=0.5,
        epsilon=1.0,
        dist_func="absolute_error",
        sum_stat="Identity",
        model=None,
        random_seed=-1,
        chain=0,
    ):

        self.draws = draws
        self.kernel = kernel
        self.n_steps = n_steps
        self.start = start
        self.tune_steps = tune_steps
        self.p_acc_rate = p_acc_rate
        self.threshold = threshold
        self.epsilon = epsilon
        self.dist_func = dist_func
        self.sum_stat = sum_stat
        self.model = model
        self.random_seed = random_seed
        self.chain = chain

        self.model = modelcontext(model)

        if self.random_seed != -1:
            np.random.seed(self.random_seed)

        self.beta = 0
        self.max_steps = n_steps
        self.proposed = draws * n_steps
        self.acc_rate = 1
        self.acc_per_chain = np.ones(self.draws)
        self.variables = inputvars(self.model.vars)
        self.dimension = sum(v.dsize for v in self.variables)
        self.scalings = np.ones(self.draws) * 2.38 / (self.dimension) ** 0.5
        self.weights = np.ones(self.draws) / self.draws
        self.log_marginal_likelihood = 0

    def initialize_population(self):
        """
        Create an initial population from the prior distribution
        """
        population = []
        var_info = OrderedDict()
        if self.start is None:
            init_rnd = sample_prior_predictive(
                self.draws, var_names=[v.name for v in self.model.unobserved_RVs], model=self.model,
            )
        else:
            init_rnd = self.start

        init = self.model.test_point

        for v in self.variables:
            var_info[v.name] = (init[v.name].shape, init[v.name].size)

        for i in range(self.draws):

            point = Point({v.name: init_rnd[v.name][i] for v in self.variables}, model=self.model)
            population.append(self.model.dict_to_array(point))

        self.posterior = np.array(floatX(population))
        self.var_info = var_info

    def setup_kernel(self):
        """
        Set up the likelihood logp function based on the chosen kernel
        """
        shared = make_shared_replacements(self.variables, self.model)
        self.prior_logp_func = logp_forw([self.model.varlogpt], self.variables, shared)

        if self.kernel.lower() == "abc":
            simulator = self.model.observed_RVs[0]
            self.likelihood_logp_func = PseudoLikelihood(
                self.epsilon,
                simulator.observations,
                simulator.distribution.function,
                [v.name for v in simulator.distribution.params],
                self.model,
                self.var_info,
                self.variables,
                self.dist_func,
                self.sum_stat,
            )
        elif self.kernel.lower() == "metropolis":
            self.likelihood_logp_func = logp_forw([self.model.datalogpt], self.variables, shared)

    def initialize_logp(self):
        """
        initialize the prior and likelihood log probabilities
        """
        priors = [self.prior_logp_func(sample) for sample in self.posterior]
        likelihoods = [self.likelihood_logp_func(sample) for sample in self.posterior]

        self.prior_logp = np.array(priors).squeeze()
        self.likelihood_logp = np.array(likelihoods).squeeze()

    def update_weights_beta(self):
        """
        Calculate the next inverse temperature (beta), the importance weights based on current beta
        and tempered likelihood and updates the marginal likelihood estimation
        """
        low_beta = old_beta = self.beta
        up_beta = 2.0
        rN = int(len(self.likelihood_logp) * self.threshold)

        while up_beta - low_beta > 1e-6:
            new_beta = (low_beta + up_beta) / 2.0
            log_weights_un = (new_beta - old_beta) * self.likelihood_logp
            log_weights = log_weights_un - logsumexp(log_weights_un)
            ESS = int(np.exp(-logsumexp(log_weights * 2)))
            if ESS == rN:
                break
            elif ESS < rN:
                up_beta = new_beta
            else:
                low_beta = new_beta
        if new_beta >= 1:
            new_beta = 1
            log_weights_un = (new_beta - old_beta) * self.likelihood_logp
            log_weights = log_weights_un - logsumexp(log_weights_un)

        self.log_marginal_likelihood += logsumexp(log_weights_un) - np.log(self.draws)
        self.beta = new_beta
        self.weights = np.exp(log_weights)

    def resample(self):
        """
        Resample particles based on importance weights
        """
        resampling_indexes = np.random.choice(
            np.arange(self.draws), size=self.draws, p=self.weights
        )

        self.posterior = self.posterior[resampling_indexes]
        self.prior_logp = self.prior_logp[resampling_indexes]
        self.likelihood_logp = self.likelihood_logp[resampling_indexes]
        self.posterior_logp = self.prior_logp + self.likelihood_logp * self.beta
        self.acc_per_chain = self.acc_per_chain[resampling_indexes]
        self.scalings = self.scalings[resampling_indexes]

    def update_proposal(self):
        """
        Update proposal based on the covariance matrix from tempered posterior
        """
        cov = np.cov(self.posterior, ddof=0, aweights=self.weights, rowvar=0)
        cov = np.atleast_2d(cov)
        cov += 1e-6 * np.eye(cov.shape[0])
        if np.isnan(cov).any() or np.isinf(cov).any():
            raise ValueError('Sample covariances not valid! Likely "draws" is too small!')
        self.cov = cov

    def tune(self):
        """
        Tune scaling and n_steps based on the acceptance rate.
        """
        ave_scaling = np.exp(np.log(self.scalings.mean()) + (self.acc_per_chain.mean() - 0.234))
        self.scalings = 0.5 * (
            ave_scaling + np.exp(np.log(self.scalings) + (self.acc_per_chain - 0.234))
        )

        if self.tune_steps:
            acc_rate = max(1.0 / self.proposed, self.acc_rate)
            self.n_steps = min(
                self.max_steps, max(2, int(np.log(1 - self.p_acc_rate) / np.log(1 - acc_rate))),
            )

        self.proposed = self.draws * self.n_steps

    def mutate(self):
        ac_ = np.empty((self.n_steps, self.draws))

        proposals = (
            np.random.multivariate_normal(
                np.zeros(self.dimension), self.cov, size=(self.n_steps, self.draws)
            )
            * self.scalings[:, None]
        )
        log_R = np.log(np.random.rand(self.n_steps, self.draws))

        for n_step in range(self.n_steps):
            proposal = floatX(self.posterior + proposals[n_step])
            ll = np.array([self.likelihood_logp_func(prop) for prop in proposal])
            pl = np.array([self.prior_logp_func(prop) for prop in proposal])
            proposal_logp = pl + ll * self.beta
            accepted = log_R[n_step] < (proposal_logp - self.posterior_logp)
            ac_[n_step] = accepted
            self.posterior[accepted] = proposal[accepted]
            self.posterior_logp[accepted] = proposal_logp[accepted]
            self.prior_logp[accepted] = pl[accepted]
            self.likelihood_logp[accepted] = ll[accepted]

        self.acc_per_chain = np.mean(ac_, axis=0)
        self.acc_rate = np.mean(ac_)

    def posterior_to_trace(self):
        """
        Save results into a PyMC3 trace
        """
        lenght_pos = len(self.posterior)
        varnames = [v.name for v in self.variables]

        with self.model:
            strace = NDArray(self.model)
            strace.setup(lenght_pos, self.chain)
        for i in range(lenght_pos):
            value = []
            size = 0
            for var in varnames:
                shape, new_size = self.var_info[var]
                value.append(self.posterior[i][size : size + new_size].reshape(shape))
                size += new_size
            strace.record(point={k: v for k, v in zip(varnames, value)})
        return strace


def logp_forw(out_vars, vars, shared):
    """Compile Theano function of the model and the input and output variables.

    Parameters
    ----------
    out_vars: List
        containing :class:`pymc3.Distribution` for the output variables
    vars: List
        containing :class:`pymc3.Distribution` for the input variables
    shared: List
        containing :class:`theano.tensor.Tensor` for depended shared data
    """
    out_list, inarray0 = join_nonshared_inputs(out_vars, vars, shared)
    f = theano_function([inarray0], out_list[0])
    f.trust_input = True
    return f


class PseudoLikelihood:
    """
    Pseudo Likelihood
    """

    def __init__(
        self,
        epsilon,
        observations,
        function,
        params,
        model,
        var_info,
        variables,
        distance,
        sum_stat,
    ):
        """
        epsilon: float
            Standard deviation of the gaussian pseudo likelihood.
        observations: array-like
            observed data
        function: python function
            data simulator
        params: list
            names of the variables parameterizing the simulator.
        model: PyMC3 model
        var_info: dict
            generated by ``SMC.initialize_population``
        distance : str or callable
            Distance function. The only available option is ``gaussian_kernel``
        sum_stat: str or callable
            Summary statistics. Available options are ``indentity``, ``sorted``, ``mean``,
            ``median``. The user can pass any valid Python function
        """
        self.epsilon = epsilon
        self.function = function
        self.params = params
        self.model = model
        self.var_info = var_info
        self.variables = variables
        self.varnames = [v.name for v in self.variables]
        self.unobserved_RVs = [v.name for v in self.model.unobserved_RVs]
        self.get_unobserved_fn = self.model.fastfn(self.model.unobserved_RVs)

        if sum_stat == "identity":
            self.sum_stat = lambda x: x
        elif sum_stat == "sorted":
            self.sum_stat = np.sort
        elif sum_stat == "mean":
            self.sum_stat = np.mean
        elif sum_stat == "median":
            self.sum_stat = np.median
        elif hasattr(sum_stat, "__call__"):
            self.sum_stat = sum_stat
        else:
            raise ValueError(f"The summary statistics {sum_stat} is not implemented")

        self.observations = self.sum_stat(observations)

        if distance == "gaussian_kernel":
            self.distance = self.gaussian_kernel
        elif hasattr(distance, "__call__"):
            self.distance = distance
        else:
            raise ValueError(f"The distance metric {distance} is not implemented")

    def posterior_to_function(self, posterior):
        model = self.model
        var_info = self.var_info

        varvalues = []
        samples = {}
        size = 0
        for var in self.variables:
            shape, new_size = var_info[var.name]
            varvalues.append(posterior[size : size + new_size].reshape(shape))
            size += new_size
        point = {k: v for k, v in zip(self.varnames, varvalues)}
        for varname, value in zip(self.unobserved_RVs, self.get_unobserved_fn(point)):
            if varname in self.params:
                samples[varname] = value
        return samples

    def gaussian_kernel(self, obs_data, sim_data):
        return np.sum(-0.5 * ((obs_data - sim_data) / self.epsilon) ** 2)

    def __call__(self, posterior):
        func_parameters = self.posterior_to_function(posterior)
        sim_data = self.sum_stat(self.function(**func_parameters))
        return self.distance(self.observations, sim_data)
