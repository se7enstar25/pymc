""" Test database backends """

from numpy.testing import TestCase, assert_array_equal, assert_equal
from pymc import MCMC
import pymc.database as database
from pymc.examples import DisasterModel
import os,sys
import numpy as np

class test_backend_attribution(TestCase):
    def test_raise(self):
        self.assertRaises(AttributeError, MCMC, DisasterModel, 'heysugar')
    def test_import(self):
        self.assertRaises(ImportError, MCMC, DisasterModel, '__test_import__')


class test_no_trace(TestCase):
    def test(self):
        M = MCMC(DisasterModel, db='no_trace')
        M.sample(1000,500,2)
        try:
            assert_array_equal(M.e.trace().shape, (0,))
        except AttributeError:
            pass
        
class test_ram(TestCase):
    def test(self):
        M = MCMC(DisasterModel, db='ram')
        M.sample(500,100,2)
        assert_array_equal(M.e.trace().shape, (200,))
        assert_equal(M.e.trace.length(), 200)
        M.sample(100)
        assert_array_equal(M.e.trace().shape, (100,))
        assert_array_equal(M.e.trace(chain=None).shape, (300,))
        
class test_txt(TestCase):
    def test(self):
        try:
            os.removedir('txt_data')
        except:
            pass
        S = MCMC(DisasterModel, db='txt', dirname='txt_data', mode='w')
        S.sample(100)
        S.sample(100)
        S.db.close()
    
    def test_load(self):
        db = database.txt.load('txt_data')
        assert_equal(len(db.e._trace), 2)
        assert_array_equal(db.e().shape, (100,))
        assert_array_equal(db.e(chain=None).shape, (200,))
        S = MCMC(DisasterModel, db)
        S.sample(100)
        S.db.close()
        
        
        
class test_pickle(TestCase):
    def __init__(*args, **kwds):
        TestCase.__init__(*args, **kwds)
        try: 
            os.remove('Disaster.pickle')
        except:
            pass
            
    def test(self):
        M = MCMC(DisasterModel, db='pickle', name='Disaster')
        M.sample(500,100,2)
        assert_array_equal(M.e.trace().shape, (200,))
        assert_equal(M.e.trace.length(), 200)
        M.db.close()
        
    def test_load(self):
        db = database.pickle.load('Disaster.pickle')
        S = MCMC(DisasterModel, db)
        S.sample(100,0,1)
        assert_equal(len(S.e.trace._trace),2)
        assert_array_equal(S.e.trace().shape, (100,))
        assert_array_equal(S.e.trace(chain=None).shape, (300,))
        assert_equal(S.e.trace.length(None), 300)
        S.db.close()

##class test_mysql(TestCase):
##    def test(self):
##        M = MCMC(DisasterModel, db='mysql')
##        M.sample(300,100,2)
##    
if hasattr(database, 'sqlite'):
    class test_sqlite(TestCase):
        def __init__(*args, **kwds):
            TestCase.__init__(*args, **kwds)
            try:    
                os.remove('Disaster.sqlite')
                os.remove('Disaster.sqlite-journal')
            except:
                pass
                
        def test(self):
            M = MCMC(DisasterModel, db='sqlite', name='Disaster')
            M.sample(500,100,2)
            assert_array_equal(M.e.trace().shape, (200,))
            # Test second trace.
            M.sample(100,0,1)
            assert_array_equal(M.e.trace().shape, (100,))
            assert_array_equal(M.e.trace(chain=None).shape, (300,))
            assert_equal(M.e.trace.length(chain=1), 200)
            assert_equal(M.e.trace.length(chain=2), 100)
            assert_equal(M.e.trace.length(chain=None), 300)
            assert_equal(M.e.trace.length(chain=-1), 100)
            M.sample(50)
            assert_equal(M.e.trace.length(), 50)
            M.db.close()
            
            
        def test_load(self):
            db = database.sqlite.load('Disaster.sqlite')
            assert_array_equal(db.e.length(chain=1), 200)
            assert_array_equal(db.e.length(chain=2), 100)
            assert_array_equal(db.e.length(chain=3), 50)
            assert_array_equal(db.e.length(chain=None), 350)
            S = MCMC(DisasterModel, db)
            S.sample(100,0,1)
            assert_array_equal(S.e.trace(chain=-1).shape, (100,))
            assert_array_equal(S.e.trace(chain=None).shape, (450,))
            S.db.close()
        
if hasattr(database, 'hdf5'):
    class test_hdf5(TestCase):
        def __init__(*args, **kwds):
            TestCase.__init__(*args, **kwds)        
            try: 
                os.remove('Disaster.hdf5')
            except:
                pass
        
        def test(self):
            S = MCMC(DisasterModel, db='hdf5', name='Disaster')
            S.sample(500,100,2)
            assert_array_equal(S.e.trace().shape, (200,))
            assert_equal(S.e.trace.length(), 200)
            assert_array_equal(S.D.value, DisasterModel.D_array)
            S.db.close()
            
        def test_load(self):
            db = database.hdf5.load('Disaster.hdf5', 'a')
            assert_array_equal(db._h5file.root.chain1.PyMCsamples.attrs.D, 
               DisasterModel.D_array)
            assert_array_equal(db.D, DisasterModel.D_array)
            S = MCMC(DisasterModel, db)
            
            S.sample(100,0,1)
            assert_array_equal(S.e.trace(chain=None).shape, (300,))
            assert_equal(S.e.trace.length(None), 300)
            db.close() # For some reason, the hdf5 file remains open.
            S.db.close()
            
            # test that the step method state was correctly restored.
            sm = S.step_methods.pop()
            assert(sm._accepted+sm._rejected ==600)
            
        def test_mode(self):
            S = MCMC(DisasterModel, db='hdf5', name='Disaster', mode='w')
            try:
                tables = S.db._gettable(None)
            except LookupError:
                pass
            else:
                raise 'Mode not working'
            S.sample(100)
            S.db.close()
            S = MCMC(DisasterModel, db='hdf5', name='Disaster', mode='a')
            tables = S.db._gettable(None)
            assert_equal(len(tables), 1)
            S.db.close()
            
        def test_compression(self):
            try: 
                os.remove('DisasterModelCompressed.hdf5')
            except:
                pass
            db = database.hdf5.Database('DisasterModelCompressed.hdf5', complevel=5)
            S = MCMC(DisasterModel,db)
            S.sample(450,100,1)
            assert_array_equal(S.e.trace().shape, (350,))
            S.db.close()
            db.close()
            
        def test_attribute_assignement(self):
            arr = np.array([[1,2],[3,4]])
            db = database.hdf5.load('Disaster.hdf5', 'a')
            db.add_attr('some_list', [1,2,3])
            db.add_attr('some_dict', {'a':5})
            db.add_attr('some_array', arr, array=True)
            assert_array_equal(db.some_list, [1,2,3])
            assert_equal(db.some_dict['a'], 5)
            assert_array_equal(db.some_array.read(), arr)
            db.close()
            del db
            db = database.hdf5.load('Disaster.hdf5', 'a')
            assert_array_equal(db.some_list, [1,2,3])
            assert_equal(db.some_dict['a'], 5)
            assert_array_equal(db.some_array, arr)
            db.close()
        
if __name__ == '__main__':
    import unittest
    unittest.main()
    try:
        S.db.close()
    except:
        pass
