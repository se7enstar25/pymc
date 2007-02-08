#/usr/bin/env python  
try:
    import setuptools
except ImportError:
    pass
from numpy.distutils.core import setup, Extension

# Compile flib (fortran source for statistical distributions.)

flib = Extension(name='PyMC2.flib',sources=['PyMC2/flib.f'])
ext_modules = [flib]

# Compile base objects in C
try:
    PyMCObjects = Extension(name='PyMC2.PyMCObjects', sources = [    'PyMC2/PyMCObjects/PyMCBase.c',
                                                                'PyMC2/PyMCObjects/Parameter.c',
                                                                'PyMC2/PyMCObjects/Node.c',
                                                                'PyMC2/PyMCObjects/RemoteProxy.c',
                                                                'PyMC2/PyMCObjects/PyMCObjects.c'])
    ext_modules.append(PyMCObjects)
except:
    print 'Not able to compile C objects, falling back to pure python.'
    
distrib = setup(
    name="PyMC2",
    version="2.0",
    description = "PyMC version 2.0",
    license="Academic Free License",
    url="trichech.us",
    packages=["PyMC2", "PyMC2.database", "PyMC2.tests", "PyMC2.examples", 
    "PyMC2.MultiModelInference"],
    ext_modules = ext_modules    
)
