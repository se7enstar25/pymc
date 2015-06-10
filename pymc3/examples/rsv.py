import pymc3 as pm
import numpy as np

# 1-year-old children in Jordan
kids = np.array([180489, 191817, 190830])
# Proportion of population in Amman
amman_prop = 0.35
# infant RSV cases in Al Bashir hostpital
rsv_cases = np.array([40, 59, 65])

with pm.Model() as model:

    # Al Bashir hospital market share
    market_share = pm.Uniform('market_share', 0.5, 0.6)

    # Number of 1 y.o. in Amman
    n_amman = pm.Binomial('n_amman', kids, amman_prop, shape=3)

    # Prior probability
    prev_rsv = pm.Beta('prev_rsv', 1, 5, shape=3)

    # RSV in Amman
    y_amman = pm.Binomial('y_amman', n_amman, prev_rsv, shape=3, testval=100)

    # Likelihood for number with RSV in hospital (assumes Pr(hosp | RSV) = 1)
    y_hosp = pm.Binomial('y_hosp', y_amman, market_share, observed=rsv_cases)


    

def run(n=1000): 
    if n == "short":
        n = 50
    with model:
        trace = pm.sample(10000, step=[pm.NUTS(), pm.Metropolis()]) 

if __name__ == '__main__':
    run()


