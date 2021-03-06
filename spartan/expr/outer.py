from .base import Expr
import numpy as np
from spartan.node import Node
from traits.api import Instance, Dict, Function, PythonValue, HasTraits


class OuterProductExpr(Expr):
  chidlren = Instance(Expr) 
  map_fn = Function 
  map_fn_kw = PythonValue 
  reduce_fn = PythonValue 
  reduce_fn_kw = PythonValue 

def outer_product(a, b, map_fn, reduce_fn):
  '''
  Outer (cartesian) product over the tiles of ``a`` and ``b``.
  
  ``map_fn`` is applied to each pair; ``reduce_fn`` is used to 
  combine overlapping outputs.
  
  :param a:
  :param b:
  '''
  return OuterProductExpr(a, b, map_fn, reduce_fn)

def outer(a, b):
  return OuterProductExpr(a, b, map_fn=np.dot, 
                          reduce_fn=np.add)
