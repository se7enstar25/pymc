#/usr/bin/env python  

try:
    import setuptools
except ImportError:
    pass

from numpy.distutils.misc_util import Configuration
from numpy.distutils.system_info import get_info
config = Configuration('PyMC2',parent_package=None,top_path=None)

# If optimized lapack/ BLAS libraries are present, compile distributions that involve linear algebra against those.
try:
    lapack_info = get_info('lapack_opt',1)
    config.add_extension(name='flib',sources=['PyMC2/flib.f',
    'PyMC2/histogram.f', 'PyMC2/flib_blas.f', 'PyMC2/math.f'], extra_info=lapack_info)
except:
    config.add_extension(name='flib',sources=['PyMC2/flib.f', 'PyMC2/histogram.f', 'PyMC2/math.f'])
    
    
# Try to compile the Pyrex version of LazyFunction
try:
    config.add_extension(name='PyrexLazyFunction',sources=['PyMC2/PyrexLazyFunction.c'])
except:
    pass

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(  version="2.0",
            description = "PyMC version 2.0",
            license="Academic Free License",
            packages=["PyMC2", "PyMC2.database", "PyMC2.examples", "PyMC2.MultiModelInference", "PyMC2/tests"],
            url="trichech.us",
            **(config.todict()))

