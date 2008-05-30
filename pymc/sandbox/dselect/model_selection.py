import pymc
import numpy as np
from numpy import exp, log
import moments, jacobians, defaults, istat
import warnings


"""
Bayesian Distribution Selection                 
===============================                 
                                                
:author: David Huard                            
:date: May 7, 2008                              
:institution: McGill University, Montreal, Qc, Canada
                                                
                                                
Introduction                                    
------------                                    
 
This module implements a function that, given a dataset,  selects the `best` 
statistical distributions among a set. 
                       
Finding the statistical distribution best suited for describing a particular 
dataset is part art part science. Decision trees exist, that can help identify 
the appropriate distribution by answering to some elementary questions.
.. image:: figs/decision_tree.jpg
                       
Chi square.            
                       
Of course, simply fitting the Maximum Likelihood parameters and compare the
likelihoods of different distributions will lead to spurious results since 
the likelihood is very much dependent on the whole shape of the distribution
and its number of parameters. 
       
       
Concept
-------

Here, the idea is to apply Bayesian model selection to select the best model 
(the statistical distribution). That is, we compute

.. math::
    W_i \prop p(M_i | data, I) 
    
where `W_i` stands for the weight of each distribution, :math:`M_i` the 
different models, and `I` the prior information on the data. The way we solve 
this equation is by inserting the distribution parameters as latent variables:

.. math:: 
    p(M_i |data, I) & = \int p(M_i, \theta_i | data, I) d\theta_i \\
                    & = \int p(data | M_i, \theta_i) \pi(\theta_i | I).
     
Now :math:`p(data | M_i, \theta_i)` is simply the likelihood, but we still
need to define :math:`\pi(\theta | I)`. The way this is done here is by defining
a prior distribution on X :math:`I : \pi(x)`. This pdf is used to evaluate the 
probability of the parameters :math:`\theta_i` by the following manner: 
 
 1. N random values (r) are drawn from distribution :math:`M_i` using 
    :math:`\theta_i`.
 2. The likelihood of `r` is evaluated using :math:`\pi(r)` and assigned to 
    the parameters :math:`\theta_i`. 


The whole procedure can be implemented easily using pymc's MCMC algorithms. 
The MCMC sampler will explore the parameter space and return a trace that 
corresponds a random sample drawn from :math:`\pi(\theta_i | I)`. This sample
can then be used to compute :math:`E(p(data | M_i, \theta_i)`, which provides 
the weight of model `i`.

Usage
-----


"""


def builder(data, distributions, xprior, initial_params={}):
    """Return a MCMC model selection sampler.
    
    Parameters
    ---------
    data : array
      Data set used to select the distribution.
    distributions : sequence 
      A collection of Stochastic instances.
      For each given function, there has to be an entry in moments, jacobians 
      and defaults with the same __name__ as the distribution.
      Basically, all we really need is a random method, a log probability
      and default initial values. We should eventually let users define objects
      that have those attributes.
    xprior : function(x)
      Function returning the log probability density of x. This is a prior 
      estimate of the shape of the distribution.
    weights : sequence
      The prior probability assigned to each distribution in distributions.
    default_params : dict
      A dictionary of initial parameters for the distribution. 
    """  

    # 1. Extract the relevant information about each distribution:
    # name, random generating function, log probability and default parameters.
    names=[]; random_f={}; logp_f={}; init_val={}
    for d in distributions:
        name = d.__name__.lower()
                
        if d.__module__ == 'pymc.distributions':
            random = getattr(pymc, 'r%s'%name)
            logp = getattr(pymc, name+'_like')
            initial_values = istat.guess_params_from_sample(data, name)
            
        elif d.__module__ == 'pymc.ScipyDistributions':
            raise ValueError, 'Scipy distributions not yet supported.'
            
        else:
            try:
                random = d.random
                logp = d.logp
                initial_values = d.defaults
            except:
                raise ValueError, 'Unrecognized distribution %s'%d.__str__()
        
        if initial_values is None:
            raise ValueError, 'Distribution %s not supported. Skipping.'%name
            
        
        names.append(name)
        random_f[name] = random
        logp_f[name] = logp
        init_val[name] = initial_values
        init_val.update(initial_params)
        
    # 2. Define the various latent variables and their priors
    nr = 10
    latent= {}
    for name in names:
        def prior(value):
            """Prior density for the parameters.
            This function draws random values from the distribution 
            parameterized with values. The probability of these random values
            is then computed using xprior."""
            r = random_f[name](size=nr, *value)
            if np.any(np.isnan(r)):
                return -np.inf
            lp = xprior(r)
            return lp
            
        value = np.array(init_val[name])
        try:
            latent['%s_params'%name] = pymc.Stochastic(logp = prior,
                doc = 'Prior for the parameters of the %s distribution'%name,
                name = '%s_params'%name,
                parents = {},
                value = value,
                )
        except ValueError:
            raise ValueError, 'It seems that the initial parameters for distribution %s yield a zero probability according to prior_x.'%name

    # 3. Compute the probability for each model
    lprob = {}
    for name in names:
        def logp(params):
            lp = logp_f[name](data, *params)
            return lp

        lprob['%s_logp'%name] = pymc.Deterministic(eval=logp,
                doc = 'Likelihood of the dataset given the distribution and the parameters.',
                name = '%s_logp'%name,
                parents = {'params':latent['%s_params'%name]})
    
    input = latent
    input.update(lprob)
    input[names] = names
    M = pymc.MCMC(input=input)
    #for name in names:
        #M.use_step_method(pymc.AdaptiveMetropolis, input['%s_params'%name], verbose=3)
    return M
        
        
def select_distribution(data, distributions, xprior, weights=None, initial_params={}):

    # 1. Define the prior for the distributions. 
    N = len(distributions)
    if weights is None:
        weights = np.ones(N)/N
    else:
        assert(np.sum(weights) ==1.)        
       
    # 2. Create the MCMC sampler and sample
    M = builder(data, distributions, xprior, initial_params)
    iter = 10000*N
    tune = iter/5
    M.sample(iter, tune)
    
    # 3. Compute the weights
    for name in names:
        dtrm = getattr(M, '%s_logp'%name)
        W[name] = np.mean(np.exp(dtrm.trace()))
        
    return W
    
        
        

def test_builder():
    from numpy import random
    return builder(random.normal(3,4,10), [pymc.Beta, pymc.Normal], lambda x: pymc.uniform_like(x, 0, 100), initial_params={'normal':np.array([50.,1.])})

def test_selection():
    N = 40
    r = pymc.rexponential(2.0, size=N)
    def prior_x(x, L=5):
        """Triangle distribution.
        A = h*L/2 = 1
        """
        h = 2./L
        if np.all(0.< x) and np.all(x < L):
            return np.sum(log(h - h/L *x))
        else:
            return -np.inf
        
    W = select_distribution(r, [pymc.Exponential, pymc.Weibull, pymc.Cauchy, pymc.Chi2, pymc.Exponential, pymc.Exponweib], prior_x)
    return W
