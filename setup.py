#/usr/bin/env python  

try:
    import setuptools
except ImportError:
    pass

from numpy.distutils.misc_util import Configuration
from numpy.distutils.system_info import get_info
import os
config = Configuration('pymc',parent_package=None,top_path=None)

# If optimized lapack/ BLAS libraries are present, compile distributions that involve linear algebra against those.
# Otherwise compile blas and lapack from netlib sources.
lapack_info = get_info('lapack_opt',1)
f_sources = ['pymc/flib.f','pymc/histogram.f', 'pymc/flib_blas.f', 'pymc/math.f', 'pymc/gibbsit.f']
if lapack_info:
    config.add_extension(name='flib',sources=f_sources, extra_info=lapack_info)
else:
    for fname in os.listdir('blas'):
        if fname[:-2]=='.f':
            f_sources.append('blas/'+fname)
    for fname in os.listdir('lapack'):
        if fname[:-2]=='.f':
            f_sources.append('lapack/'+fname)        
    config.add_extension(name='flib',sources=f_sources)
    
# Try to compile the Pyrex version of LazyFunction
config.add_extension(name='LazyFunction',sources=['pymc/LazyFunction.c'])
config.add_extension(name='Container_values', sources='pymc/Container_values.c')

config_dict = config.todict()
try:
    config_dict.pop('packages')
except:
    pass

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(  version="2.0",
            description = "PyMC version 2.0",
            license="Academic Free License",
            packages=["pymc", "pymc/database", "pymc/examples", "pymc/MultiModelInference", "pymc/tests"],
            url="trichech.us",
            **(config_dict))

