/* Generated by Pyrex 0.9.5.1a on Sat Oct  6 14:18:30 2007 */

#include "Python.h"
#include "structmember.h"
#ifndef PY_LONG_LONG
  #define PY_LONG_LONG LONG_LONG
#endif
#ifdef __cplusplus
#define __PYX_EXTERN_C extern "C"
#else
#define __PYX_EXTERN_C extern
#endif
__PYX_EXTERN_C double pow(double, double);
#include "numpy/ndarrayobject.h"


typedef struct {PyObject **p; char *s;} __Pyx_InternTabEntry; /*proto*/
typedef struct {PyObject **p; char *s; long n;} __Pyx_StringTabEntry; /*proto*/

static PyObject *__pyx_m;
static PyObject *__pyx_b;
static int __pyx_lineno;
static char *__pyx_filename;
static char **__pyx_f;

static PyObject *__Pyx_Import(PyObject *name, PyObject *from_list); /*proto*/

static int __Pyx_InternStrings(__Pyx_InternTabEntry *t); /*proto*/

static void __Pyx_AddTraceback(char *funcname); /*proto*/

/* Declarations from Container_values */



/* Implementation of Container_values */


static PyObject *__pyx_n_Variable;
static PyObject *__pyx_n_ContainerBase;
static PyObject *__pyx_n_copy;
static PyObject *__pyx_n_ndarray;
static PyObject *__pyx_n_array;
static PyObject *__pyx_n_zeros;
static PyObject *__pyx_n_shape;
static PyObject *__pyx_n_arange;
static PyObject *__pyx_n_where;
static PyObject *__pyx_n_LTCValue;
static PyObject *__pyx_n_DCValue;
static PyObject *__pyx_n_OCValue;
static PyObject *__pyx_n_ACValue;
static PyObject *__pyx_n_Node;
static PyObject *__pyx_n_numpy;

static PyObject *__pyx_n_val_ind;
static PyObject *__pyx_n_nonval_ind;
static PyObject *__pyx_n__value;
static PyObject *__pyx_n_n_val;
static PyObject *__pyx_n_value;
static PyObject *__pyx_n_n_nonval;

static PyObject *__pyx_f_16Container_values_LTCValue(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds); /*proto*/
static char __pyx_doc_16Container_values_LTCValue[] = "\n    Fills in a list/tuple container\'s value.\n    \n    :SeeAlso: ListTupleContainer\n    ";
static PyObject *__pyx_f_16Container_values_LTCValue(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds) {
  PyObject *__pyx_v_container = 0;
  int __pyx_v_i;
  int __pyx_v_ind;
  PyObject *__pyx_v__value;
  PyObject *__pyx_v_val_ind;
  PyObject *__pyx_v_nonval_ind;
  PyObject *__pyx_r;
  PyObject *__pyx_1 = 0;
  long __pyx_2;
  PyObject *__pyx_3 = 0;
  int __pyx_4;
  static char *__pyx_argnames[] = {"container",0};
  if (!PyArg_ParseTupleAndKeywords(__pyx_args, __pyx_kwds, "O", __pyx_argnames, &__pyx_v_container)) return 0;
  Py_INCREF(__pyx_v_container);
  __pyx_v__value = Py_None; Py_INCREF(Py_None);
  __pyx_v_val_ind = Py_None; Py_INCREF(Py_None);
  __pyx_v_nonval_ind = Py_None; Py_INCREF(Py_None);

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":17 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n_val_ind); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 17; goto __pyx_L1;}
  Py_DECREF(__pyx_v_val_ind);
  __pyx_v_val_ind = __pyx_1;
  __pyx_1 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":18 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n_nonval_ind); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 18; goto __pyx_L1;}
  Py_DECREF(__pyx_v_nonval_ind);
  __pyx_v_nonval_ind = __pyx_1;
  __pyx_1 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":19 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n__value); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 19; goto __pyx_L1;}
  Py_DECREF(__pyx_v__value);
  __pyx_v__value = __pyx_1;
  __pyx_1 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":21 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n_n_val); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 21; goto __pyx_L1;}
  __pyx_2 = PyInt_AsLong(__pyx_1); if (PyErr_Occurred()) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 21; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  for (__pyx_v_i = 0; __pyx_v_i < __pyx_2; ++__pyx_v_i) {

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":22 */
    __pyx_1 = PyInt_FromLong(__pyx_v_i); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 22; goto __pyx_L1;}
    __pyx_3 = PyObject_GetItem(__pyx_v_val_ind, __pyx_1); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 22; goto __pyx_L1;}
    Py_DECREF(__pyx_1); __pyx_1 = 0;
    __pyx_4 = PyInt_AsLong(__pyx_3); if (PyErr_Occurred()) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 22; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    __pyx_v_ind = __pyx_4;

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":23 */
    __pyx_1 = PyInt_FromLong(__pyx_v_ind); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 23; goto __pyx_L1;}
    __pyx_3 = PyObject_GetItem(__pyx_v_container, __pyx_1); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 23; goto __pyx_L1;}
    Py_DECREF(__pyx_1); __pyx_1 = 0;
    __pyx_1 = PyObject_GetAttr(__pyx_3, __pyx_n_value); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 23; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    __pyx_3 = PyInt_FromLong(__pyx_v_ind); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 23; goto __pyx_L1;}
    if (PyObject_SetItem(__pyx_v__value, __pyx_3, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 23; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    Py_DECREF(__pyx_1); __pyx_1 = 0;
  }

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":24 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n_n_nonval); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 24; goto __pyx_L1;}
  __pyx_2 = PyInt_AsLong(__pyx_1); if (PyErr_Occurred()) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 24; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  for (__pyx_v_i = 0; __pyx_v_i < __pyx_2; ++__pyx_v_i) {

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":25 */
    __pyx_3 = PyInt_FromLong(__pyx_v_i); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 25; goto __pyx_L1;}
    __pyx_1 = PyObject_GetItem(__pyx_v_nonval_ind, __pyx_3); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 25; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    __pyx_4 = PyInt_AsLong(__pyx_1); if (PyErr_Occurred()) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 25; goto __pyx_L1;}
    Py_DECREF(__pyx_1); __pyx_1 = 0;
    __pyx_v_ind = __pyx_4;

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":26 */
    __pyx_3 = PyInt_FromLong(__pyx_v_ind); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 26; goto __pyx_L1;}
    __pyx_1 = PyObject_GetItem(__pyx_v_container, __pyx_3); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 26; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    __pyx_3 = PyInt_FromLong(__pyx_v_ind); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 26; goto __pyx_L1;}
    if (PyObject_SetItem(__pyx_v__value, __pyx_3, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 26; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    Py_DECREF(__pyx_1); __pyx_1 = 0;
  }

  __pyx_r = Py_None; Py_INCREF(Py_None);
  goto __pyx_L0;
  __pyx_L1:;
  Py_XDECREF(__pyx_1);
  Py_XDECREF(__pyx_3);
  __Pyx_AddTraceback("Container_values.LTCValue");
  __pyx_r = 0;
  __pyx_L0:;
  Py_DECREF(__pyx_v__value);
  Py_DECREF(__pyx_v_val_ind);
  Py_DECREF(__pyx_v_nonval_ind);
  Py_DECREF(__pyx_v_container);
  return __pyx_r;
}

static PyObject *__pyx_n_val_keys;
static PyObject *__pyx_n_nonval_keys;

static PyObject *__pyx_f_16Container_values_DCValue(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds); /*proto*/
static char __pyx_doc_16Container_values_DCValue[] = "\n    Fills in a dictionary container\'s value.\n    \n    :SeeAlso: DictContainer\n    ";
static PyObject *__pyx_f_16Container_values_DCValue(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds) {
  PyObject *__pyx_v_container = 0;
  int __pyx_v_i;
  PyObject *__pyx_v__value;
  PyObject *__pyx_v_val_keys;
  PyObject *__pyx_v_nonval_keys;
  PyObject *__pyx_v_key;
  PyObject *__pyx_r;
  PyObject *__pyx_1 = 0;
  long __pyx_2;
  PyObject *__pyx_3 = 0;
  static char *__pyx_argnames[] = {"container",0};
  if (!PyArg_ParseTupleAndKeywords(__pyx_args, __pyx_kwds, "O", __pyx_argnames, &__pyx_v_container)) return 0;
  Py_INCREF(__pyx_v_container);
  __pyx_v__value = Py_None; Py_INCREF(Py_None);
  __pyx_v_val_keys = Py_None; Py_INCREF(Py_None);
  __pyx_v_nonval_keys = Py_None; Py_INCREF(Py_None);
  __pyx_v_key = Py_None; Py_INCREF(Py_None);

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":37 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n_val_keys); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 37; goto __pyx_L1;}
  Py_DECREF(__pyx_v_val_keys);
  __pyx_v_val_keys = __pyx_1;
  __pyx_1 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":38 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n_nonval_keys); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 38; goto __pyx_L1;}
  Py_DECREF(__pyx_v_nonval_keys);
  __pyx_v_nonval_keys = __pyx_1;
  __pyx_1 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":39 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n__value); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 39; goto __pyx_L1;}
  Py_DECREF(__pyx_v__value);
  __pyx_v__value = __pyx_1;
  __pyx_1 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":41 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n_n_val); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 41; goto __pyx_L1;}
  __pyx_2 = PyInt_AsLong(__pyx_1); if (PyErr_Occurred()) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 41; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  for (__pyx_v_i = 0; __pyx_v_i < __pyx_2; ++__pyx_v_i) {

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":42 */
    __pyx_1 = PyInt_FromLong(__pyx_v_i); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 42; goto __pyx_L1;}
    __pyx_3 = PyObject_GetItem(__pyx_v_val_keys, __pyx_1); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 42; goto __pyx_L1;}
    Py_DECREF(__pyx_1); __pyx_1 = 0;
    Py_DECREF(__pyx_v_key);
    __pyx_v_key = __pyx_3;
    __pyx_3 = 0;

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":43 */
    __pyx_1 = PyObject_GetItem(__pyx_v_container, __pyx_v_key); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 43; goto __pyx_L1;}
    __pyx_3 = PyObject_GetAttr(__pyx_1, __pyx_n_value); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 43; goto __pyx_L1;}
    Py_DECREF(__pyx_1); __pyx_1 = 0;
    if (PyObject_SetItem(__pyx_v__value, __pyx_v_key, __pyx_3) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 43; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
  }

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":44 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n_n_nonval); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 44; goto __pyx_L1;}
  __pyx_2 = PyInt_AsLong(__pyx_1); if (PyErr_Occurred()) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 44; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  for (__pyx_v_i = 0; __pyx_v_i < __pyx_2; ++__pyx_v_i) {

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":45 */
    __pyx_3 = PyInt_FromLong(__pyx_v_i); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 45; goto __pyx_L1;}
    __pyx_1 = PyObject_GetItem(__pyx_v_nonval_keys, __pyx_3); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 45; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    Py_DECREF(__pyx_v_key);
    __pyx_v_key = __pyx_1;
    __pyx_1 = 0;

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":46 */
    __pyx_3 = PyObject_GetItem(__pyx_v_container, __pyx_v_key); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 46; goto __pyx_L1;}
    if (PyObject_SetItem(__pyx_v__value, __pyx_v_key, __pyx_3) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 46; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
  }

  __pyx_r = Py_None; Py_INCREF(Py_None);
  goto __pyx_L0;
  __pyx_L1:;
  Py_XDECREF(__pyx_1);
  Py_XDECREF(__pyx_3);
  __Pyx_AddTraceback("Container_values.DCValue");
  __pyx_r = 0;
  __pyx_L0:;
  Py_DECREF(__pyx_v__value);
  Py_DECREF(__pyx_v_val_keys);
  Py_DECREF(__pyx_v_nonval_keys);
  Py_DECREF(__pyx_v_key);
  Py_DECREF(__pyx_v_container);
  return __pyx_r;
}

static PyObject *__pyx_n__dict_container;
static PyObject *__pyx_n___dict__;

static PyObject *__pyx_f_16Container_values_OCValue(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds); /*proto*/
static char __pyx_doc_16Container_values_OCValue[] = "\n    Fills in an object container\'s value.\n    \n    :SeeAlso: ObjectContainer\n    ";
static PyObject *__pyx_f_16Container_values_OCValue(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds) {
  PyObject *__pyx_v_container = 0;
  int __pyx_v_i;
  PyObject *__pyx_v__value;
  PyObject *__pyx_v_val_keys;
  PyObject *__pyx_v_nonval_keys;
  PyObject *__pyx_v_key;
  PyObject *__pyx_v__dict_container;
  PyObject *__pyx_r;
  PyObject *__pyx_1 = 0;
  PyObject *__pyx_2 = 0;
  long __pyx_3;
  static char *__pyx_argnames[] = {"container",0};
  if (!PyArg_ParseTupleAndKeywords(__pyx_args, __pyx_kwds, "O", __pyx_argnames, &__pyx_v_container)) return 0;
  Py_INCREF(__pyx_v_container);
  __pyx_v__value = Py_None; Py_INCREF(Py_None);
  __pyx_v_val_keys = Py_None; Py_INCREF(Py_None);
  __pyx_v_nonval_keys = Py_None; Py_INCREF(Py_None);
  __pyx_v_key = Py_None; Py_INCREF(Py_None);
  __pyx_v__dict_container = Py_None; Py_INCREF(Py_None);

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":57 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n__dict_container); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 57; goto __pyx_L1;}
  Py_DECREF(__pyx_v__dict_container);
  __pyx_v__dict_container = __pyx_1;
  __pyx_1 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":58 */
  __pyx_1 = PyObject_GetAttr(__pyx_v__dict_container, __pyx_n_val_keys); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 58; goto __pyx_L1;}
  Py_DECREF(__pyx_v_val_keys);
  __pyx_v_val_keys = __pyx_1;
  __pyx_1 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":59 */
  __pyx_1 = PyObject_GetAttr(__pyx_v__dict_container, __pyx_n_nonval_keys); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 59; goto __pyx_L1;}
  Py_DECREF(__pyx_v_nonval_keys);
  __pyx_v_nonval_keys = __pyx_1;
  __pyx_1 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":60 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n__value); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 60; goto __pyx_L1;}
  __pyx_2 = PyObject_GetAttr(__pyx_1, __pyx_n___dict__); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 60; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  Py_DECREF(__pyx_v__value);
  __pyx_v__value = __pyx_2;
  __pyx_2 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":63 */
  __pyx_1 = PyObject_GetAttr(__pyx_v__dict_container, __pyx_n_n_val); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 63; goto __pyx_L1;}
  __pyx_3 = PyInt_AsLong(__pyx_1); if (PyErr_Occurred()) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 63; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  for (__pyx_v_i = 0; __pyx_v_i < __pyx_3; ++__pyx_v_i) {

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":64 */
    __pyx_2 = PyInt_FromLong(__pyx_v_i); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 64; goto __pyx_L1;}
    __pyx_1 = PyObject_GetItem(__pyx_v_val_keys, __pyx_2); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 64; goto __pyx_L1;}
    Py_DECREF(__pyx_2); __pyx_2 = 0;
    Py_DECREF(__pyx_v_key);
    __pyx_v_key = __pyx_1;
    __pyx_1 = 0;

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":65 */
    __pyx_2 = PyObject_GetItem(__pyx_v__dict_container, __pyx_v_key); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 65; goto __pyx_L1;}
    __pyx_1 = PyObject_GetAttr(__pyx_2, __pyx_n_value); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 65; goto __pyx_L1;}
    Py_DECREF(__pyx_2); __pyx_2 = 0;
    if (PyObject_SetItem(__pyx_v__value, __pyx_v_key, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 65; goto __pyx_L1;}
    Py_DECREF(__pyx_1); __pyx_1 = 0;
  }

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":66 */
  __pyx_2 = PyObject_GetAttr(__pyx_v__dict_container, __pyx_n_n_nonval); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 66; goto __pyx_L1;}
  __pyx_3 = PyInt_AsLong(__pyx_2); if (PyErr_Occurred()) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 66; goto __pyx_L1;}
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  for (__pyx_v_i = 0; __pyx_v_i < __pyx_3; ++__pyx_v_i) {

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":67 */
    __pyx_1 = PyInt_FromLong(__pyx_v_i); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 67; goto __pyx_L1;}
    __pyx_2 = PyObject_GetItem(__pyx_v_nonval_keys, __pyx_1); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 67; goto __pyx_L1;}
    Py_DECREF(__pyx_1); __pyx_1 = 0;
    Py_DECREF(__pyx_v_key);
    __pyx_v_key = __pyx_2;
    __pyx_2 = 0;

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":68 */
    __pyx_1 = PyObject_GetItem(__pyx_v__dict_container, __pyx_v_key); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 68; goto __pyx_L1;}
    if (PyObject_SetItem(__pyx_v__value, __pyx_v_key, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 68; goto __pyx_L1;}
    Py_DECREF(__pyx_1); __pyx_1 = 0;
  }

  __pyx_r = Py_None; Py_INCREF(Py_None);
  goto __pyx_L0;
  __pyx_L1:;
  Py_XDECREF(__pyx_1);
  Py_XDECREF(__pyx_2);
  __Pyx_AddTraceback("Container_values.OCValue");
  __pyx_r = 0;
  __pyx_L0:;
  Py_DECREF(__pyx_v__value);
  Py_DECREF(__pyx_v_val_keys);
  Py_DECREF(__pyx_v_nonval_keys);
  Py_DECREF(__pyx_v_key);
  Py_DECREF(__pyx_v__dict_container);
  Py_DECREF(__pyx_v_container);
  return __pyx_r;
}

static PyObject *__pyx_n__ravelledvalue;
static PyObject *__pyx_n__ravelleddata;

static PyObject *__pyx_f_16Container_values_ACValue(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds); /*proto*/
static char __pyx_doc_16Container_values_ACValue[] = "\n    Fills in an array container\'s value.\n    \n    :SeeAlso: ArrayContainer\n    ";
static PyObject *__pyx_f_16Container_values_ACValue(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds) {
  PyObject *__pyx_v_container = 0;
  int __pyx_v_i;
  long __pyx_v_ind;
  PyObject *__pyx_v_val_ind;
  PyObject *__pyx_v_nonval_ind;
  PyObject *__pyx_v_ravelledvalue;
  PyObject *__pyx_v_ravelleddata;
  PyObject *__pyx_r;
  PyObject *__pyx_1 = 0;
  long __pyx_2;
  PyObject *__pyx_3 = 0;
  long __pyx_4;
  static char *__pyx_argnames[] = {"container",0};
  if (!PyArg_ParseTupleAndKeywords(__pyx_args, __pyx_kwds, "O", __pyx_argnames, &__pyx_v_container)) return 0;
  Py_INCREF(__pyx_v_container);
  __pyx_v_val_ind = Py_None; Py_INCREF(Py_None);
  __pyx_v_nonval_ind = Py_None; Py_INCREF(Py_None);
  __pyx_v_ravelledvalue = Py_None; Py_INCREF(Py_None);
  __pyx_v_ravelleddata = Py_None; Py_INCREF(Py_None);

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":80 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n_val_ind); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 80; goto __pyx_L1;}
  Py_DECREF(__pyx_v_val_ind);
  __pyx_v_val_ind = __pyx_1;
  __pyx_1 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":81 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n_nonval_ind); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 81; goto __pyx_L1;}
  Py_DECREF(__pyx_v_nonval_ind);
  __pyx_v_nonval_ind = __pyx_1;
  __pyx_1 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":83 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n__ravelledvalue); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 83; goto __pyx_L1;}
  Py_DECREF(__pyx_v_ravelledvalue);
  __pyx_v_ravelledvalue = __pyx_1;
  __pyx_1 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":84 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n__ravelleddata); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 84; goto __pyx_L1;}
  Py_DECREF(__pyx_v_ravelleddata);
  __pyx_v_ravelleddata = __pyx_1;
  __pyx_1 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":86 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n_n_val); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 86; goto __pyx_L1;}
  __pyx_2 = PyInt_AsLong(__pyx_1); if (PyErr_Occurred()) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 86; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  for (__pyx_v_i = 0; __pyx_v_i < __pyx_2; ++__pyx_v_i) {

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":87 */
    __pyx_1 = PyInt_FromLong(__pyx_v_i); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 87; goto __pyx_L1;}
    __pyx_3 = PyObject_GetItem(__pyx_v_val_ind, __pyx_1); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 87; goto __pyx_L1;}
    Py_DECREF(__pyx_1); __pyx_1 = 0;
    __pyx_4 = PyInt_AsLong(__pyx_3); if (PyErr_Occurred()) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 87; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    __pyx_v_ind = __pyx_4;

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":88 */
    __pyx_1 = PyInt_FromLong(__pyx_v_ind); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 88; goto __pyx_L1;}
    __pyx_3 = PyObject_GetItem(__pyx_v_ravelleddata, __pyx_1); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 88; goto __pyx_L1;}
    Py_DECREF(__pyx_1); __pyx_1 = 0;
    __pyx_1 = PyObject_GetAttr(__pyx_3, __pyx_n_value); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 88; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    __pyx_3 = PyInt_FromLong(__pyx_v_ind); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 88; goto __pyx_L1;}
    if (PyObject_SetItem(__pyx_v_ravelledvalue, __pyx_3, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 88; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    Py_DECREF(__pyx_1); __pyx_1 = 0;
  }

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":90 */
  __pyx_1 = PyObject_GetAttr(__pyx_v_container, __pyx_n_n_nonval); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 90; goto __pyx_L1;}
  __pyx_4 = PyInt_AsLong(__pyx_1); if (PyErr_Occurred()) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 90; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  for (__pyx_v_i = 0; __pyx_v_i < __pyx_4; ++__pyx_v_i) {

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":91 */
    __pyx_3 = PyInt_FromLong(__pyx_v_i); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 91; goto __pyx_L1;}
    __pyx_1 = PyObject_GetItem(__pyx_v_nonval_ind, __pyx_3); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 91; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    __pyx_2 = PyInt_AsLong(__pyx_1); if (PyErr_Occurred()) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 91; goto __pyx_L1;}
    Py_DECREF(__pyx_1); __pyx_1 = 0;
    __pyx_v_ind = __pyx_2;

    /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":92 */
    __pyx_3 = PyInt_FromLong(__pyx_v_ind); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 92; goto __pyx_L1;}
    __pyx_1 = PyObject_GetItem(__pyx_v_ravelleddata, __pyx_3); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 92; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    __pyx_3 = PyInt_FromLong(__pyx_v_ind); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 92; goto __pyx_L1;}
    if (PyObject_SetItem(__pyx_v_ravelledvalue, __pyx_3, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 92; goto __pyx_L1;}
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    Py_DECREF(__pyx_1); __pyx_1 = 0;
  }

  __pyx_r = Py_None; Py_INCREF(Py_None);
  goto __pyx_L0;
  __pyx_L1:;
  Py_XDECREF(__pyx_1);
  Py_XDECREF(__pyx_3);
  __Pyx_AddTraceback("Container_values.ACValue");
  __pyx_r = 0;
  __pyx_L0:;
  Py_DECREF(__pyx_v_val_ind);
  Py_DECREF(__pyx_v_nonval_ind);
  Py_DECREF(__pyx_v_ravelledvalue);
  Py_DECREF(__pyx_v_ravelleddata);
  Py_DECREF(__pyx_v_container);
  return __pyx_r;
}

static __Pyx_InternTabEntry __pyx_intern_tab[] = {
  {&__pyx_n_ACValue, "ACValue"},
  {&__pyx_n_ContainerBase, "ContainerBase"},
  {&__pyx_n_DCValue, "DCValue"},
  {&__pyx_n_LTCValue, "LTCValue"},
  {&__pyx_n_Node, "Node"},
  {&__pyx_n_OCValue, "OCValue"},
  {&__pyx_n_Variable, "Variable"},
  {&__pyx_n___dict__, "__dict__"},
  {&__pyx_n__dict_container, "_dict_container"},
  {&__pyx_n__ravelleddata, "_ravelleddata"},
  {&__pyx_n__ravelledvalue, "_ravelledvalue"},
  {&__pyx_n__value, "_value"},
  {&__pyx_n_arange, "arange"},
  {&__pyx_n_array, "array"},
  {&__pyx_n_copy, "copy"},
  {&__pyx_n_n_nonval, "n_nonval"},
  {&__pyx_n_n_val, "n_val"},
  {&__pyx_n_ndarray, "ndarray"},
  {&__pyx_n_nonval_ind, "nonval_ind"},
  {&__pyx_n_nonval_keys, "nonval_keys"},
  {&__pyx_n_numpy, "numpy"},
  {&__pyx_n_shape, "shape"},
  {&__pyx_n_val_ind, "val_ind"},
  {&__pyx_n_val_keys, "val_keys"},
  {&__pyx_n_value, "value"},
  {&__pyx_n_where, "where"},
  {&__pyx_n_zeros, "zeros"},
  {0, 0}
};

static struct PyMethodDef __pyx_methods[] = {
  {"LTCValue", (PyCFunction)__pyx_f_16Container_values_LTCValue, METH_VARARGS|METH_KEYWORDS, __pyx_doc_16Container_values_LTCValue},
  {"DCValue", (PyCFunction)__pyx_f_16Container_values_DCValue, METH_VARARGS|METH_KEYWORDS, __pyx_doc_16Container_values_DCValue},
  {"OCValue", (PyCFunction)__pyx_f_16Container_values_OCValue, METH_VARARGS|METH_KEYWORDS, __pyx_doc_16Container_values_OCValue},
  {"ACValue", (PyCFunction)__pyx_f_16Container_values_ACValue, METH_VARARGS|METH_KEYWORDS, __pyx_doc_16Container_values_ACValue},
  {0, 0, 0, 0}
};

static void __pyx_init_filenames(void); /*proto*/

PyMODINIT_FUNC initContainer_values(void); /*proto*/
PyMODINIT_FUNC initContainer_values(void) {
  PyObject *__pyx_1 = 0;
  PyObject *__pyx_2 = 0;
  __pyx_init_filenames();
  __pyx_m = Py_InitModule4("Container_values", __pyx_methods, 0, 0, PYTHON_API_VERSION);
  if (!__pyx_m) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 1; goto __pyx_L1;};
  __pyx_b = PyImport_AddModule("__builtin__");
  if (!__pyx_b) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 1; goto __pyx_L1;};
  if (PyObject_SetAttrString(__pyx_m, "__builtins__", __pyx_b) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 1; goto __pyx_L1;};
  if (__Pyx_InternStrings(__pyx_intern_tab) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 1; goto __pyx_L1;};

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":1 */
  __pyx_1 = PyList_New(2); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 1; goto __pyx_L1;}
  Py_INCREF(__pyx_n_Variable);
  PyList_SET_ITEM(__pyx_1, 0, __pyx_n_Variable);
  Py_INCREF(__pyx_n_ContainerBase);
  PyList_SET_ITEM(__pyx_1, 1, __pyx_n_ContainerBase);
  __pyx_2 = __Pyx_Import(__pyx_n_Node, __pyx_1); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 1; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  __pyx_1 = PyObject_GetAttr(__pyx_2, __pyx_n_Variable); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 1; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_Variable, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 1; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  __pyx_1 = PyObject_GetAttr(__pyx_2, __pyx_n_ContainerBase); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 1; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_ContainerBase, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 1; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  Py_DECREF(__pyx_2); __pyx_2 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":2 */
  __pyx_2 = PyList_New(1); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 2; goto __pyx_L1;}
  Py_INCREF(__pyx_n_copy);
  PyList_SET_ITEM(__pyx_2, 0, __pyx_n_copy);
  __pyx_1 = __Pyx_Import(__pyx_n_copy, __pyx_2); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 2; goto __pyx_L1;}
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  __pyx_2 = PyObject_GetAttr(__pyx_1, __pyx_n_copy); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 2; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_copy, __pyx_2) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 2; goto __pyx_L1;}
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  Py_DECREF(__pyx_1); __pyx_1 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":3 */
  __pyx_1 = PyList_New(6); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 3; goto __pyx_L1;}
  Py_INCREF(__pyx_n_ndarray);
  PyList_SET_ITEM(__pyx_1, 0, __pyx_n_ndarray);
  Py_INCREF(__pyx_n_array);
  PyList_SET_ITEM(__pyx_1, 1, __pyx_n_array);
  Py_INCREF(__pyx_n_zeros);
  PyList_SET_ITEM(__pyx_1, 2, __pyx_n_zeros);
  Py_INCREF(__pyx_n_shape);
  PyList_SET_ITEM(__pyx_1, 3, __pyx_n_shape);
  Py_INCREF(__pyx_n_arange);
  PyList_SET_ITEM(__pyx_1, 4, __pyx_n_arange);
  Py_INCREF(__pyx_n_where);
  PyList_SET_ITEM(__pyx_1, 5, __pyx_n_where);
  __pyx_2 = __Pyx_Import(__pyx_n_numpy, __pyx_1); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 3; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  __pyx_1 = PyObject_GetAttr(__pyx_2, __pyx_n_ndarray); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 3; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_ndarray, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 3; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  __pyx_1 = PyObject_GetAttr(__pyx_2, __pyx_n_array); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 3; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_array, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 3; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  __pyx_1 = PyObject_GetAttr(__pyx_2, __pyx_n_zeros); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 3; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_zeros, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 3; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  __pyx_1 = PyObject_GetAttr(__pyx_2, __pyx_n_shape); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 3; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_shape, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 3; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  __pyx_1 = PyObject_GetAttr(__pyx_2, __pyx_n_arange); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 3; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_arange, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 3; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  __pyx_1 = PyObject_GetAttr(__pyx_2, __pyx_n_where); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 3; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_where, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 3; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  Py_DECREF(__pyx_2); __pyx_2 = 0;

  /* "/Users/anand/renearch/PyMC/PyMC2/Container_values.pyx":70 */
  return;
  __pyx_L1:;
  Py_XDECREF(__pyx_1);
  Py_XDECREF(__pyx_2);
  __Pyx_AddTraceback("Container_values");
}

static char *__pyx_filenames[] = {
  "Container_values.pyx",
};

/* Runtime support code */

static void __pyx_init_filenames(void) {
  __pyx_f = __pyx_filenames;
}

static PyObject *__Pyx_Import(PyObject *name, PyObject *from_list) {
    PyObject *__import__ = 0;
    PyObject *empty_list = 0;
    PyObject *module = 0;
    PyObject *global_dict = 0;
    PyObject *empty_dict = 0;
    PyObject *list;
    __import__ = PyObject_GetAttrString(__pyx_b, "__import__");
    if (!__import__)
        goto bad;
    if (from_list)
        list = from_list;
    else {
        empty_list = PyList_New(0);
        if (!empty_list)
            goto bad;
        list = empty_list;
    }
    global_dict = PyModule_GetDict(__pyx_m);
    if (!global_dict)
        goto bad;
    empty_dict = PyDict_New();
    if (!empty_dict)
        goto bad;
    module = PyObject_CallFunction(__import__, "OOOO",
        name, global_dict, empty_dict, list);
bad:
    Py_XDECREF(empty_list);
    Py_XDECREF(__import__);
    Py_XDECREF(empty_dict);
    return module;
}

static int __Pyx_InternStrings(__Pyx_InternTabEntry *t) {
    while (t->p) {
        *t->p = PyString_InternFromString(t->s);
        if (!*t->p)
            return -1;
        ++t;
    }
    return 0;
}

#include "compile.h"
#include "frameobject.h"
#include "traceback.h"

static void __Pyx_AddTraceback(char *funcname) {
    PyObject *py_srcfile = 0;
    PyObject *py_funcname = 0;
    PyObject *py_globals = 0;
    PyObject *empty_tuple = 0;
    PyObject *empty_string = 0;
    PyCodeObject *py_code = 0;
    PyFrameObject *py_frame = 0;
    
    py_srcfile = PyString_FromString(__pyx_filename);
    if (!py_srcfile) goto bad;
    py_funcname = PyString_FromString(funcname);
    if (!py_funcname) goto bad;
    py_globals = PyModule_GetDict(__pyx_m);
    if (!py_globals) goto bad;
    empty_tuple = PyTuple_New(0);
    if (!empty_tuple) goto bad;
    empty_string = PyString_FromString("");
    if (!empty_string) goto bad;
    py_code = PyCode_New(
        0,            /*int argcount,*/
        0,            /*int nlocals,*/
        0,            /*int stacksize,*/
        0,            /*int flags,*/
        empty_string, /*PyObject *code,*/
        empty_tuple,  /*PyObject *consts,*/
        empty_tuple,  /*PyObject *names,*/
        empty_tuple,  /*PyObject *varnames,*/
        empty_tuple,  /*PyObject *freevars,*/
        empty_tuple,  /*PyObject *cellvars,*/
        py_srcfile,   /*PyObject *filename,*/
        py_funcname,  /*PyObject *name,*/
        __pyx_lineno,   /*int firstlineno,*/
        empty_string  /*PyObject *lnotab*/
    );
    if (!py_code) goto bad;
    py_frame = PyFrame_New(
        PyThreadState_Get(), /*PyThreadState *tstate,*/
        py_code,             /*PyCodeObject *code,*/
        py_globals,          /*PyObject *globals,*/
        0                    /*PyObject *locals*/
    );
    if (!py_frame) goto bad;
    py_frame->f_lineno = __pyx_lineno;
    PyTraceBack_Here(py_frame);
bad:
    Py_XDECREF(py_srcfile);
    Py_XDECREF(py_funcname);
    Py_XDECREF(empty_tuple);
    Py_XDECREF(empty_string);
    Py_XDECREF(py_code);
    Py_XDECREF(py_frame);
}
