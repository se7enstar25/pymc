"""
The DisasterMCMC example.

"""
from __future__ import with_statement
from numpy.testing import *
from pymc import MCMC, database
from pymc.examples import disaster_model
import nose,  warnings, os

PLOT=True
try:
    from pymc.Matplot import plot, autocorrelation
except:
    PLOT=False
    pass


DIR = 'testresults/'


class test_MCMC(TestCase):

    # Instantiate samplers
    M = MCMC(disaster_model, db='pickle')

    # Sample
    M.sample(4000,2000,verbose=0, progress_bar=False)
    M.db.close()
    def test_instantiation(self):

        # Check stochastic arrays
        assert_equal(len(self.M.stochastics), 3)
        assert_equal(len(self.M.observed_stochastics),1)
        assert_array_equal(self.M.D.value, disaster_model.disasters_array)

    def test_plot(self):
        if not PLOT:
            raise nose.SkipTest

        # Plot samples
        plot(self.M.e, path=DIR, verbose=0)

    def test_autocorrelation(self):
        if not PLOT:
            raise nose.SkipTest

        # Plot samples
        autocorrelation(self.M.e, path=DIR,  verbose=0)

    def test_stats(self):
        S = self.M.e.stats()
        self.M.stats()

    def test_stats_after_reload(self):
        db = database.pickle.load('MCMC.pickle')
        M2 = MCMC(disaster_model, db=db)
        M2.stats()
        db.close()
        os.remove('MCMC.pickle')


if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',  FutureWarning)
        nose.runmodule()

