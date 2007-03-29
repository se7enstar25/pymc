"""
==========================
Database backends for PyMC
==========================

A typical MCMC run will generate thousands of samples, and some application 
requires well over 100000 iterations. Keeping all this information in memory 
can badly strain the performances of PyMC, and users will find their other 
applications slowing down. Moreover, we generally wish to store all or part 
of the sampled data for future use. To do so, PyMC offers different storing 
strategies:

  - `no_trace` : don't keep track of the samples,
  - `ram` : keep everything in RAM (default),
  - `pickle` : put traces in a dictionnary and pickle it once sampling is over.
  - `txt` : keep everything in RAM, and dump samples in txt files once 
            sampling is completed,
  - `sqlite` : store data in a sqlite database,
  - `mysql` : store data in a mysql database,
  - `hdf5` : store data in a hdf5 file, using pytables.

Although what happens under the hood is very different from one backend to 
another, from the user perspective, there is no difference whatsoever. The only 
thing that will change is the output file (if any) generated by the backend. 

Writing a new backend
---------------------

Each backend is implemented in a file in the database directory. Each one 
of these files define two classes: Trace and Database. A new backend 
can easily be implemented by defining new classes and saving them in a 
file. Look at template.py for a skeleton, and the other modules for examples. 

"""

__author__ = ["David Huard <david.huard@gmail.com>",
                "Chris Fonnesbeck"]
__version__ = "2.0.beta"

__modules__ = ["ram", "pickle", "no_trace", "txt", "sqlite", "mysql", "hdf5"]


available_modules = []
for mod in __modules__:
    try:
        exec "from %s import *" % mod
        available_modules.append(mod)
    except ImportError, msg:
        print "Database module " + mod + " could not be loaded: "
        print msg
del mod

