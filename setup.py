#/usr/bin/env python  

try:
    import setuptools
except ImportError:
    pass

from numpy.distutils.misc_util import Configuration
from numpy.distutils.system_info import get_info
import os
config = Configuration('pymc',parent_package=None,top_path=None)


# ==============================
# = Compile Fortran extensions =
# ==============================

# If optimized lapack/ BLAS libraries are present, compile distributions that involve linear algebra against those.
# Otherwise compile blas and lapack from netlib sources.
lapack_info = get_info('lapack_opt',1)
f_sources = ['pymc/flib.f','pymc/histogram.f', 'pymc/flib_blas.f', 'pymc/math.f', 'pymc/gibbsit.f']
if lapack_info:
    config.add_extension(name='flib',sources=f_sources, extra_info=lapack_info)
else:
    ##inc_dirs = ['blas/BLAS','lapack/double']
    print 'No optimized BLAS or Lapack libraries found, building from source. This may take a while...'
    for fname in os.listdir('blas/BLAS'):
        if fname[-2:]=='.f':
            f_sources.append('blas/BLAS/'+fname)
    ##    for fname in os.listdir('lapack/double'):
    ##        if fname[-2:]=='.f':
    ##            inc_dirs.append('lapack/double/'+fname)

    for fname in ['dpotrs','dpotrf','dpotf2','ilaenv','dlamch','ilaver','ieeeck','iparmq']:
        f_sources.append('lapack/double/'+fname+'.f')
    config.add_extension(name='flib',sources=f_sources)


    
# ============================
# = Compile Pyrex extensions =
# ============================

config.add_extension(name='LazyFunction',sources=['pymc/LazyFunction.c'])
config.add_extension(name='Container_values', sources='pymc/Container_values.c')

config_dict = config.todict()
try:
    config_dict.pop('packages')
except:
    pass


# ===========================================
# = Compile GP package's Fortran extensions =
# ===========================================

# Compile linear algebra utilities
if lapack_info:
    config.add_extension(name='GP.linalg_utils',sources=['pymc/GP/linalg_utils.f'], extra_info=lapack_info)
    config.add_extension(name='GP.incomplete_chol',sources=['pymc/GP/incomplete_chol.f'], extra_info=lapack_info)

else:
    print 'No optimized BLAS or Lapack libraries found, building from source. This may take a while...'
    f_sources = []
    for fname in os.listdir('blas/BLAS'):
        if fname[-2:]=='.f':
            f_sources.append('blas/BLAS/'+fname)

    for fname in ['dpotrs','dpotrf','dpotf2','ilaenv','dlamch','ilaver','ieeeck','iparmq']:
        f_sources.append('lapack/double/'+fname+'.f')

    config.add_extension(name='GP.linalg_utils',sources=['pymc/GP/linalg_utils.f'] + f_sources)
    config.add_extension(name='GP.incomplete_chol',sources=['pymc/GP/incomplete_chol.f'] + f_sources)
    

# Compile covariance functions
config.add_extension(name='GP.cov_funs.isotropic_cov_funs',\
sources=['pymc/GP/cov_funs/isotropic_cov_funs.f'],\
extra_info=lapack_info)

config.add_extension(name='GP.cov_funs.distances',sources=['pymc/GP/cov_funs/distances.f'], extra_info=lapack_info)


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(  version="2.0",
            description = "PyMC version 2.0",
            license="Academic Free License",
            packages=["pymc", "pymc/database", "pymc/examples", "pymc/MultiModelInference", "pymc/tests", "pymc/GP"],
            url="trichech.us",
            **(config_dict))

