""" Test database backends """

from numpy.testing import *
from PyMC2 import Sampler, database
from PyMC2.examples import DisasterModel
import os,sys

class test_no_trace(NumpyTestCase):
    def check(self):
        M = Sampler(DisasterModel, db='no_trace')
        M.sample(1000,500,2)
        try:
            assert_array_equal(M.e.trace().shape, (0,))
        except AttributeError:
            pass
        
class test_ram(NumpyTestCase):
    def check(self):
        M = Sampler(DisasterModel, db='ram')
        M.sample(500,100,2)
        assert_array_equal(M.e.trace().shape, (200,))
        assert_equal(M.e.trace.length(), 200)
        M.sample(100)
        assert_array_equal(M.e.trace().shape, (100,))
        assert_array_equal(M.e.trace(chain=None).shape, (300,))
        
        
class test_pickle(NumpyTestCase):
    def __init__(*args, **kwds):
        NumpyTestCase.__init__(*args, **kwds)
        try: 
            os.remove('DisasterModel.pickle')
        except:
            pass
            
    def check(self):
        M = Sampler(DisasterModel, db='pickle')
        M.sample(500,100,2)
        assert_array_equal(M.e.trace().shape, (200,))
        assert_equal(M.e.trace.length(), 200)
        M.db.close()
        
    def check_load(self):
        db = database.pickle.load('DisasterModel.pickle')
        S = Sampler(DisasterModel, db)
        S.sample(100,0,1)
        assert_equal(len(S.e.trace._trace),2)
        assert_array_equal(S.e.trace().shape, (100,))
        assert_array_equal(S.e.trace(chain=None).shape, (300,))
        assert_equal(S.e.trace.length(None), 300)
        S.db.close()
##class test_txt(NumpyTestCase):
##    def check(self):
##        M = Sampler(DisasterModel, db='txt')
##        M.sample(300,100,2)
##        assert_equal(M.e.trace().shape, (150,))
##
##class test_mysql(NumpyTestCase):
##    def check(self):
##        M = Sampler(DisasterModel, db='mysql')
##        M.sample(300,100,2)
##    
if hasattr(database, 'sqlite'):
    class test_sqlite(NumpyTestCase):
        def __init__(*args, **kwds):
            NumpyTestCase.__init__(*args, **kwds)
            try:    
                os.remove('DisasterModel.sqlite')
                os.remove('DisasterModel.sqlite-journal')
            except:
                pass
                
        def check(self):
            M = Sampler(DisasterModel, db='sqlite')
            M.sample(500,100,2)
            assert_array_equal(M.e.trace().shape, (200,))
            M.db.close()
            
        def check_load(self):
            db = database.sqlite.load('DisasterModel.sqlite')
            S = Sampler(DisasterModel, db)
            S.sample(100,0,1)
            assert_array_equal(S.e.trace(chain=-1).shape, (100,))
            assert_array_equal(S.e.trace(chain=None).shape, (300,))
            S.db.close()
        
##class test_hdf5(NumpyTestCase):
##    def check(self):
##        M = Sampler(DisasterModel, db='hdf5')
##        M.sample(300,100,2)
if hasattr(database, 'hdf5'):
    class test_hdf5(NumpyTestCase):
        def __init__(*args, **kwds):
            NumpyTestCase.__init__(*args, **kwds)        
            try: 
                os.remove('DisasterModel.hdf5')
            except:
                pass
        
        def check(self):
            S = Sampler(DisasterModel, db='hdf5')
            S.sample(500,100,2)
            assert_array_equal(S.e.trace().shape, (200,))
            assert_equal(S.e.trace.length(), 200)
            assert_array_equal(S.D.value, DisasterModel.D_array)
            S.db.close()
            
        def check_load(self):
            db = database.hdf5.load('DisasterModel.hdf5', 'a')
            assert_array_equal(db._h5file.root.chain1.PyMCsamples.attrs.D, 
               DisasterModel.D_array)
            assert_array_equal(db.D, DisasterModel.D_array)
            S = Sampler(DisasterModel, db)
            
            S.sample(100,0,1)
            assert_array_equal(S.e.trace(chain=None).shape, (300,))
            assert_equal(S.e.trace.length(None), 300)
            S.db.close()
            
        def check_compression(self):
            try: 
                os.remove('DisasterModelCompressed.hdf5')
            except:
                pass
            db = database.hdf5.Database('DisasterModelCompressed.hdf5', complevel=5)
            S = Sampler(DisasterModel,db)
            S.sample(450,100,1)
            assert_array_equal(S.e.trace().shape, (350,))
            S.db.close()
            db.close()
        
if __name__ == '__main__':
    NumpyTest().run()
    try:
        S.db.close()
    except:
        pass
