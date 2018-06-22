import shutil
import tempfile

from .checks import close_to
from .models import (simple_categorical, mv_simple, mv_simple_discrete,
                     mv_prior_simple, simple_2model_continuous)
from pymc3.sampling import assign_step_methods, sample
from pymc3.model import Model
from pymc3.step_methods import (NUTS, BinaryGibbsMetropolis, CategoricalGibbsMetropolis,
                                Metropolis, Slice, CompoundStep, NormalProposal,
                                MultivariateNormalProposal, HamiltonianMC,
                                EllipticalSlice, smc, DEMetropolis)
from pymc3.theanof import floatX
from pymc3.distributions import (
    Binomial, Normal, Bernoulli, Categorical, Beta, HalfNormal)

from numpy.testing import assert_array_almost_equal
import numpy as np
import numpy.testing as npt
import pytest
import theano
import theano.tensor as tt
from .helpers import select_by_precision


class TestStepMethods(object):  # yield test doesn't work subclassing object
    master_samples = {
        Slice: np.array([
            -5.95252353e-01, -1.81894861e-01, -4.98211488e-01,
            -1.02262800e-01, -4.26726030e-01, 1.75446860e+00,
            -1.30022548e+00, 8.35658004e-01, 8.95879638e-01,
            -8.85214481e-01, -6.63530918e-01, -8.39303080e-01,
            9.42792225e-01, 9.03554344e-01, 8.45254684e-01,
            -1.43299803e+00, 9.04897201e-01, -1.74303131e-01,
            -6.38611581e-01, 1.50013968e+00, 1.06864438e+00,
            -4.80484421e-01, -7.52199709e-01, 1.95067495e+00,
            -3.67960104e+00, 2.49291588e+00, -2.11039152e+00,
            1.61674758e-01, -1.59564182e-01, 2.19089873e-01,
            1.88643940e+00, 4.04098154e-01, -4.59352326e-01,
            -9.06370675e-01, 5.42817654e-01, 6.99040611e-03,
            1.66396391e-01, -4.74549281e-01, 8.19064437e-02,
            1.69689952e+00, -1.62667304e+00, 1.61295808e+00,
            1.30099144e+00, -5.46722750e-01, -7.87745494e-01,
            7.91027521e-01, -2.35706976e-02, 1.68824376e+00,
            7.10566880e-01, -7.23551374e-01, 8.85613069e-01,
            -1.27300146e+00, 1.80274430e+00, 9.34266276e-01,
            2.40427061e+00, -1.85132552e-01, 4.47234196e-01,
            -9.81894859e-01, -2.83399706e-01, 1.84717533e+00,
            -1.58593284e+00, 3.18027270e-02, 1.40566006e+00,
            -9.45758714e-01, 1.18813188e-01, -1.19938604e+00,
            -8.26038466e-01, 5.03469984e-01, -4.72742758e-01,
            2.27820946e-01, -1.02608915e-03, -6.02507158e-01,
            7.72739682e-01, 7.16064505e-01, -1.63693490e+00,
            -3.97161966e-01, 1.17147944e+00, -2.87796982e+00,
            -1.59533297e+00, 6.73096114e-01, -3.34397247e-01,
            1.22357427e-01, -4.57299104e-02, 1.32005771e+00,
            -1.29910645e+00, 8.16168850e-01, -1.47357594e+00,
            1.34688446e+00, 1.06377551e+00, 4.34296696e-02,
            8.23143354e-01, 8.40906324e-01, 1.88596864e+00,
            5.77120694e-01, 2.71732927e-01, -1.36217979e+00,
            2.41488213e+00, 4.68298379e-01, 4.86342250e-01,
            -8.43949966e-01]),
        HamiltonianMC: np.array([
             0.40608634,  0.40608634,  0.04610354, -0.78588609,  0.03773683,
            -0.49373368,  0.21708042,  0.21708042, -0.14413517, -0.68284611,
             0.76299659,  0.24128663,  0.24128663, -0.54835464, -0.84408365,
            -0.82762589, -0.67429432, -0.67429432, -0.57900517, -0.97138029,
            -0.37809745, -0.37809745, -0.19333181, -0.40329098,  0.54999765,
             1.171515  ,  0.90279792,  0.90279792,  1.63830503, -0.90436674,
            -0.02516293, -0.02516293, -0.22177082, -0.28061216, -0.10158021,
             0.0807234 ,  0.16994063,  0.16994063,  0.4141503 ,  0.38505666,
            -0.25936504,  2.12074192,  2.24467132,  0.9628703 , -1.37044749,
             0.32983336, -0.55317525, -0.55317525, -0.40295662, -0.40295662,
            -0.40295662,  0.49076931,  0.04234407, -1.0002905 ,  0.99823615,
             0.99823615,  0.24915904, -0.00965061,  0.48519377,  0.21959942,
            -0.93094702, -0.93094702, -0.76812553, -0.73699981, -0.91834134,
            -0.91834134,  0.79522886, -0.04267669, -0.04267669,  0.51368761,
             0.51368761,  0.02255577,  0.70823409,  0.70823409,  0.73921198,
             0.30295007,  0.30295007,  0.30295007, -0.1300897 ,  0.44310964,
            -1.35839961, -1.55398633, -0.57323153, -0.57323153, -1.15435458,
            -0.17697793, -0.17697793,  0.2925856 , -0.56119025, -0.15360141,
             0.83715916, -0.02340449, -0.02340449, -0.63074456, -0.82745942,
            -0.67626237,  1.13814805, -0.81857813, -0.81857813,  0.26367166]),
        Metropolis: np.array([
            1.62434536, 1.01258895, 0.4844172, -0.58855142, 1.15626034, 0.39505344, 1.85716138,
            -0.20297933, -0.20297933, -0.20297933, -0.20297933, -1.08083775, -1.08083775,
            0.06388596, 0.96474191, 0.28101405, 0.01312597, 0.54348144, -0.14369126, -0.98889691,
            -0.98889691, -0.75448121, -0.94631676, -0.94631676, -0.89550901, -0.89550901,
            -0.77535005, -0.15814694, 0.14202338, -0.21022647, -0.4191207, 0.16750249, 0.45308981,
            1.33823098, 1.8511608, 1.55306796, 1.55306796, 1.55306796, 1.55306796, 0.15657163,
            0.3166087, 0.3166087, 0.3166087, 0.3166087, 0.54670343, 0.54670343, 0.32437529,
            0.12361722, 0.32191694, 0.44092559, 0.56274686, 0.56274686, 0.18746191, 0.18746191,
            -0.15639177, -0.11279491, -0.11279491, -0.11279491, -1.20770676, -1.03832432,
            -0.29776787, -1.25146848, -1.25146848, -0.93630908, -0.5857631, -0.5857631,
            -0.62445861, -0.62445861, -0.64907557, -0.64907557, -0.64907557, 0.58708846,
            -0.61217957, 0.25116575, 0.25116575, 0.80170324, 1.59451011, 0.97097938, 1.77284041,
            1.81940771, 1.81940771, 1.81940771, 1.81940771, 1.95710892, 2.18960348, 2.18960348,
            2.18960348, 2.18960348, 2.63096792, 2.53081269, 2.5482221, 1.42620337, 0.90910891,
            -0.08791792, 0.40729341, 0.23259025, 0.23259025, 0.23259025, 2.76091595, 2.51228118]),
        NUTS: np.array(
            [  1.11832371e+00,   1.11832371e+00,   1.11203151e+00,  -1.08526075e+00,
               2.58200798e-02,   2.03527183e+00,   4.47644923e-01,   8.95141642e-01,
               7.21867642e-01,   8.61681133e-01,   8.61681133e-01,   3.42001064e-01,
              -1.08109692e-01,   1.89399407e-01,   2.76571728e-01,   2.76571728e-01,
              -7.49542468e-01,  -7.25272156e-01,  -5.49940424e-01,  -5.49940424e-01,
               4.39045553e-01,  -9.79313191e-04,   4.08678631e-02,   4.08678631e-02,
              -1.17303762e+00,   4.15335470e-01,   4.80458006e-01,   5.98022153e-02,
               5.26508851e-01,   5.26508851e-01,   6.24759070e-01,   4.55268819e-01,
               8.70608570e-01,   6.56151353e-01,   6.56151353e-01,   1.29968043e+00,
               2.41336915e-01,  -7.78824784e-02,  -1.15368193e+00,  -4.92562283e-01,
              -5.16903724e-02,   4.05389240e-01,   4.05389240e-01,   4.20147769e-01,
               6.88161155e-01,   6.59273169e-01,  -4.28987827e-01,  -4.28987827e-01,
              -4.44203783e-01,  -4.61330842e-01,  -5.23216216e-01,  -1.52821368e+00,
               9.84049809e-01,   9.84049809e-01,   1.02081403e+00,  -5.60272679e-01,
               4.18620552e-01,   1.92542517e+00,   1.12029984e+00,   6.69152820e-01,
               1.56325611e+00,   6.64640934e-01,  -7.43157898e-01,  -7.43157898e-01,
              -3.18049839e-01,   6.87248073e-01,   6.90665184e-01,   1.63009949e+00,
              -4.84972607e-01,  -1.04859669e+00,   8.26455763e-01,  -1.71696305e+00,
              -1.39964174e+00,  -3.87677130e-01,  -1.85966115e-01,  -1.85966115e-01,
               4.54153291e-01,  -8.41705332e-01,  -8.46831314e-01,  -8.46831314e-01,
              -1.57419678e-01,  -3.89604101e-01,   8.15315055e-01,   2.81141081e-03,
               2.81141081e-03,   3.25839131e-01,   1.33638823e+00,   1.59391112e+00,
              -3.91174647e-01,  -2.60664979e+00,  -2.27637534e+00,  -2.81505065e+00,
              -2.24238542e+00,  -1.01648100e+00,  -1.01648100e+00,  -7.60912865e-01,
               1.44384812e+00,   2.07355127e+00,   1.91390340e+00,   1.66559696e+00]),
        smc.SMC: np.array(
      [ 0.94245927,  0.04320349,  0.16616453, -0.42667441, -0.49780471,
        0.65384837, -0.25387836,  0.38232654,  0.62490342, -0.21777828,
       -0.70756665,  0.9310788 , -0.03941721, -1.20854932,  0.39442244,
        0.24306076, -0.98310433,  2.2503327 ,  0.54090823,  0.51685018,
       -1.32968792,  0.02445827, -0.62052594, -0.28014643,  0.75977904,
       -1.20233021, -1.80432242, -0.31547627, -0.33392375, -1.34380736,
        1.44597486, -0.15871648, -0.20727832,  0.99115736,  0.3445085 ,
       -0.89909578, -0.36983042,  0.16734659,  0.13228431, -0.16786514,
       -0.36268027,  0.13369353, -1.28444377,  1.2644179 , -0.47877275,
       -0.4411035 ,  0.35735115, -1.27425973, -0.43213873,  0.70698702,
       -0.7805279 , -1.67705636, -0.10661104, -0.59947856,  0.02693047,
       -1.09062222, -0.73592286, -1.56822784,  0.97077952, -0.02149393,
       -0.26597767, -0.38710878, -0.09971606, -0.52523725,  1.64000249,
       -0.1287883 ,  0.09555045,  0.04258323, -0.16771237,  0.79324588,
       -0.4439878 , -0.00328163,  0.01267578,  0.31817545, -2.48389205,
       -0.43794095, -0.18922707,  0.0042956 ,  0.29387263,  0.66119344,
       -0.98277349,  0.4039511 ,  0.13542066, -0.78467059, -0.24334413,
       -0.62519786, -0.79586084, -0.06190844,  0.11355637,  0.66110093,
       -2.10383759,  0.48608459, -0.47993295,  0.46791254,  2.01963317,
        0.12975299,  1.71604836, -0.09413096,  0.30744711,  0.15079852,
        0.31349994,  0.26575959,  0.763656  , -1.81526952, -0.22984443,
        1.10531065,  0.26065936, -0.22274362, -0.20853456,  0.32741584,
        0.08521911, -1.53866503,  0.28501159, -0.39016642,  0.09505455,
       -0.72955337,  1.46268494,  0.56252715, -1.63048738,  1.45718808,
       -0.01141763,  0.65826932,  1.8723026 ,  0.90744555,  1.40586042,
        1.58765986,  0.06792152, -0.71397153,  0.22718523, -1.90281392,
        0.58708453, -0.77195137, -0.56979511, -0.6543881 , -1.3711677 ,
       -1.72706576, -0.41484231,  0.17460229,  0.74160523,  0.10991525,
        0.50297247,  1.04762338, -0.69148618,  1.23291629, -0.49797445,
       -0.24914585,  1.44290113, -0.23288806, -1.15495976,  0.63230627,
       -1.06229509,  0.18047975, -1.23701009,  0.10994274, -0.81730888,
        0.01827404, -0.22824212, -0.76809243, -1.36315643,  0.76097799,
        1.51091188,  0.46931765,  1.27261922,  0.98191306,  0.80721561,
        1.12844558,  1.86799414,  0.29913787, -1.49977561,  0.7551137 ,
       -1.0622067 , -0.46200335, -0.10271276, -0.63924651,  1.56074961,
       -0.53611858, -0.23229769, -0.74455411, -2.41567262, -0.96658159,
       -0.08795562,  0.08532369, -1.56005584, -0.99356212,  0.32678269,
       -0.87012306,  0.83897514,  0.9799229 , -1.27565975, -0.25761179,
        0.34968085, -0.95045095,  0.95192797, -1.5101461 ,  0.04042998,
       -0.91145107, -0.91700215,  0.0825614 ,  0.59658604,  0.64933802]),
    }

    def setup_class(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    @pytest.mark.xfail(condition=(theano.config.floatX == "float32"), reason="Fails on float32")
    def test_sample_exact(self):
        for step_method in self.master_samples:
            self.check_trace(step_method)

    def check_trace(self, step_method):
        """Tests whether the trace for step methods is exactly the same as on master.

        Code changes that effect how random numbers are drawn may change this, and require
        `master_samples` to be updated, but such changes should be noted and justified in the
        commit.

        This method may also be used to benchmark step methods across commits, by running, for
        example

        ```
        BENCHMARK=100000 ./scripts/test.sh -s pymc3/tests/test_step.py:TestStepMethods
        ```

        on multiple commits.
        """
        n_steps = 100
        with Model() as model:
            x = Normal('x', mu=0, sd=1)
            if step_method.__name__ == 'SMC':
                trace = sample(draws=200,
                               chains=2,
                               start=[{'x':1.}, {'x':-1.}],
                               random_seed=1,
                               progressbar=False,
                               step=step_method(),
                               step_kwargs={'homepath': self.temp_dir})
            elif step_method.__name__ == 'NUTS':
                step = step_method(scaling=model.test_point)
                trace = sample(0, tune=n_steps,
                               discard_tuned_samples=False,
                               step=step, random_seed=1, chains=1)
            else:
                trace = sample(0, tune=n_steps,
                               discard_tuned_samples=False,
                               step=step_method(), random_seed=1, chains=1)
        assert_array_almost_equal(
            trace.get_values('x'),
            self.master_samples[step_method],
            decimal=select_by_precision(float64=6, float32=4))

    def check_stat(self, check, trace, name):
        for (var, stat, value, bound) in check:
            s = stat(trace[var][2000:], axis=0)
            close_to(s, value, bound)

    def test_step_continuous(self):
        start, model, (mu, C) = mv_simple()
        unc = np.diag(C) ** .5
        check = (('x', np.mean, mu, unc / 10.),
                 ('x', np.std, unc, unc / 10.))
        with model:
            steps = (
                Slice(),
                HamiltonianMC(scaling=C, is_cov=True, blocked=False),
                NUTS(scaling=C, is_cov=True, blocked=False),
                Metropolis(S=C, proposal_dist=MultivariateNormalProposal, blocked=True),
                Slice(blocked=True),
                HamiltonianMC(scaling=C, is_cov=True),
                NUTS(scaling=C, is_cov=True),
                CompoundStep([
                    HamiltonianMC(scaling=C, is_cov=True),
                    HamiltonianMC(scaling=C, is_cov=True, blocked=False)]),
            )
        for step in steps:
            trace = sample(0, tune=8000, chains=1,
                           discard_tuned_samples=False, step=step,
                           start=start, model=model, random_seed=1)
            self.check_stat(check, trace, step.__class__.__name__)

    def test_step_discrete(self):
        if theano.config.floatX == "float32":
            return  # Cannot use @skip because it only skips one iteration of the yield
        start, model, (mu, C) = mv_simple_discrete()
        unc = np.diag(C) ** .5
        check = (('x', np.mean, mu, unc / 10.),
                 ('x', np.std, unc, unc / 10.))
        with model:
            steps = (
                Metropolis(S=C, proposal_dist=MultivariateNormalProposal),
            )
        for step in steps:
            trace = sample(20000, tune=0, step=step, start=start, model=model,
                           random_seed=1, chains=1)
            self.check_stat(check, trace, step.__class__.__name__)

    def test_step_categorical(self):
        start, model, (mu, C) = simple_categorical()
        unc = C ** .5
        check = (('x', np.mean, mu, unc / 10.),
                 ('x', np.std, unc, unc / 10.))
        with model:
            steps = (
                CategoricalGibbsMetropolis(model.x, proposal='uniform'),
                CategoricalGibbsMetropolis(model.x, proposal='proportional'),
            )
        for step in steps:
            trace = sample(8000, tune=0, step=step, start=start, model=model, random_seed=1)
            self.check_stat(check, trace, step.__class__.__name__)

    def test_step_elliptical_slice(self):
        start, model, (K, L, mu, std, noise) = mv_prior_simple()
        unc = noise ** 0.5
        check = (('x', np.mean, mu, unc / 10.),
                 ('x', np.std, std, unc / 10.))
        with model:
            steps = (
                EllipticalSlice(prior_cov=K),
                EllipticalSlice(prior_chol=L),
            )
        for step in steps:
            trace = sample(5000, tune=0, step=step, start=start, model=model,
                           random_seed=1, chains=1)
            self.check_stat(check, trace, step.__class__.__name__)


class TestMetropolisProposal(object):
    def test_proposal_choice(self):
        _, model, _ = mv_simple()
        with model:
            s = np.ones(model.ndim)
            sampler = Metropolis(S=s)
            assert isinstance(sampler.proposal_dist, NormalProposal)
            s = np.diag(s)
            sampler = Metropolis(S=s)
            assert isinstance(sampler.proposal_dist, MultivariateNormalProposal)
            s[0, 0] = -s[0, 0]
            with pytest.raises(np.linalg.LinAlgError):
                sampler = Metropolis(S=s)

    def test_mv_proposal(self):
        np.random.seed(42)
        cov = np.random.randn(5, 5)
        cov = cov.dot(cov.T)
        prop = MultivariateNormalProposal(cov)
        samples = np.array([prop() for _ in range(10000)])
        npt.assert_allclose(np.cov(samples.T), cov, rtol=0.2)


class TestCompoundStep(object):
    samplers = (Metropolis, Slice, HamiltonianMC, NUTS, DEMetropolis)

    @pytest.mark.skipif(theano.config.floatX == "float32",
                        reason="Test fails on 32 bit due to linalg issues")
    def test_non_blocked(self):
        """Test that samplers correctly create non-blocked compound steps."""
        _, model = simple_2model_continuous()
        with model:
            for sampler in self.samplers:
                assert isinstance(sampler(blocked=False), CompoundStep)

    @pytest.mark.skipif(theano.config.floatX == "float32",
                        reason="Test fails on 32 bit due to linalg issues")
    def test_blocked(self):
        _, model = simple_2model_continuous()
        with model:
            for sampler in self.samplers:
                sampler_instance = sampler(blocked=True)
                assert not isinstance(sampler_instance, CompoundStep)
                assert isinstance(sampler_instance, sampler)


class TestAssignStepMethods(object):
    def test_bernoulli(self):
        """Test bernoulli distribution is assigned binary gibbs metropolis method"""
        with Model() as model:
            Bernoulli('x', 0.5)
            steps = assign_step_methods(model, [])
        assert isinstance(steps, BinaryGibbsMetropolis)

    def test_normal(self):
        """Test normal distribution is assigned NUTS method"""
        with Model() as model:
            Normal('x', 0, 1)
            steps = assign_step_methods(model, [])
        assert isinstance(steps, NUTS)

    def test_categorical(self):
        """Test categorical distribution is assigned categorical gibbs metropolis method"""
        with Model() as model:
            Categorical('x', np.array([0.25, 0.75]))
            steps = assign_step_methods(model, [])
        assert isinstance(steps, BinaryGibbsMetropolis)
        with Model() as model:
            Categorical('y', np.array([0.25, 0.70, 0.05]))
            steps = assign_step_methods(model, [])
        assert isinstance(steps, CategoricalGibbsMetropolis)

    def test_binomial(self):
        """Test binomial distribution is assigned metropolis method."""
        with Model() as model:
            Binomial('x', 10, 0.5)
            steps = assign_step_methods(model, [])
        assert isinstance(steps, Metropolis)

    def test_normal_nograd_op(self):
        """Test normal distribution without an implemented gradient is assigned slice method"""
        with Model() as model:
            x = Normal('x', 0, 1)

            # a custom Theano Op that does not have a grad:
            is_64 = theano.config.floatX == "float64"
            itypes = [tt.dscalar] if is_64 else [tt.fscalar]
            otypes = [tt.dscalar] if is_64 else [tt.fscalar]
            @theano.as_op(itypes, otypes)
            def kill_grad(x):
                return x

            data = np.random.normal(size=(100,))
            Normal("y", mu=kill_grad(x), sd=1, observed=data.astype(theano.config.floatX))

            steps = assign_step_methods(model, [])
        assert isinstance(steps, Slice)


class TestPopulationSamplers(object):

    steppers = [DEMetropolis]

    def test_checks_population_size(self):
        """Test that population samplers check the population size."""
        with Model() as model:
            n = Normal('n', mu=0, sd=1)
            for stepper in TestPopulationSamplers.steppers:
                step = stepper()
                with pytest.raises(ValueError):
                    trace = sample(draws=100, chains=1, step=step)
                trace = sample(draws=100, chains=4, step=step)
        pass

    def test_parallelized_chains_are_random(self):
        with Model() as model:
            x = Normal('x', 0, 1)
            for stepper in TestPopulationSamplers.steppers:
                step = stepper()

                trace = sample(chains=4, draws=20, tune=0, step=DEMetropolis(),
                               parallelize=True)
                samples = np.array(trace.get_values('x', combine=False))[:,5]

                assert len(set(samples)) == 4, 'Parallelized {} ' \
                    'chains are identical.'.format(stepper)
        pass


@pytest.mark.xfail(condition=(theano.config.floatX == "float32"), reason="Fails on float32")
class TestNutsCheckTrace(object):
    def test_multiple_samplers(self, caplog):
        with Model():
            prob = Beta('prob', alpha=5., beta=3.)
            Binomial('outcome', n=1, p=prob)
            caplog.clear()
            sample(3, tune=2, discard_tuned_samples=False,
                   n_init=None, chains=1)
            messages = [msg.msg for msg in caplog.records]
            assert all('boolean index did not' not in msg for msg in messages)

    def test_bad_init(self):
        with Model():
            HalfNormal('a', sd=1, testval=-1, transform=None)
            with pytest.raises(ValueError) as error:
                sample(init=None)
            error.match('Bad initial')

    def test_linalg(self, caplog):
        with Model():
            a = Normal('a', shape=2)
            a = tt.switch(a > 0, np.inf, a)
            b = tt.slinalg.solve(floatX(np.eye(2)), a)
            Normal('c', mu=b, shape=2)
            caplog.clear()
            trace = sample(20, init=None, tune=5, chains=2)
            warns = [msg.msg for msg in caplog.records]
            assert np.any(trace['diverging'])
            assert (
                any('divergences after tuning' in warn
                    for warn in warns)
                or
                any('only diverging samples' in warn
                    for warn in warns))

            with pytest.raises(ValueError) as error:
                trace.report.raise_ok()
            error.match('issues during sampling')

            assert not trace.report.ok
