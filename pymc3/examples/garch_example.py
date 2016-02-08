from pymc3 import Normal, sample, Model, Bound
import theano.tensor as tt
import numpy as np
import math
"""
Example from STAN
// GARCH(1,1)

data {
  int<lower=0> T;
  real r[T];
  real<lower=0> sigma1;
}
parameters {
  real mu;
  real<lower=0> alpha0;
  real<lower=0,upper=1> alpha1;
  real<lower=0, upper=(1-alpha1)> beta1;
}
transformed parameters {
  real<lower=0> sigma[T];
  sigma[1] <- sigma1;
  for (t in 2:T)
    sigma[t] <- sqrt(alpha0
                     + alpha1 * pow(r[t-1] - mu, 2)
                     + beta1 * pow(sigma[t-1], 2));
}
model {
  r ~ normal(mu,sigma);
}
"""
T = 8
r = np.array([28,  8, -3,  7, -1,  1, 18, 12])
sigma1 = np.array([15, 10, 16, 11,  9, 11, 10, 18])
alpha0 = np.array([10, 10, 16, 8,  9, 11, 12, 18])

with Model() as garch:

    alpha1 = Normal('alpha1', 0, 1, shape=T)
    BoundedNormal = Bound(Normal, upper=(1-alpha1))
    beta1 = BoundedNormal('beta1', 0, sd=1e6)
    mu = Normal('mu', 0, sd=1e6)

    theta = tt.sqrt(alpha0 + alpha1*tt.pow(r - mu, 2) + beta1 * tt.pow(sigma1, 2))

    obs = Normal('obs', mu, sd=theta, observed=r)

def run(n=1000):
    if n == "short":
        n = 50
    with garch:
        tr = sample(n)

if __name__ == '__main__':
    run()