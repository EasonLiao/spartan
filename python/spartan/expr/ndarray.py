from .base import Expr
from .node import Node
from spartan.dense import tile, distarray
import numpy as np

class NdArrayExpr(Expr, Node):
  _members = ['_shape', 'dtype', 'tile_hint', 'combine_fn', 'reduce_fn']
  
  def visit(self, visitor):
    return NdArrayExpr(_shape=visitor.visit(self.shape),
                       dtype=visitor.visit(self.dtype),
                       tile_hint=self.tile_hint,
                       combine_fn=self.combine_fn,
                       reduce_fn=self.reduce_fn)
  
  def dependencies(self):
    return {}
  
  def compute_shape(self):
    return self._shape
 
  def evaluate(self, ctx, deps):
    shape = self._shape
    dtype = self.dtype
    tile_hint = self.tile_hint
    
    if self.combine_fn is not None:
      combiner = tile.TileAccum(self.combine_fn)
    else:
      combiner = None
      
    if self.reduce_fn is not None:
      reducer = tile.TileAccum(self.reduce_fn)
    else:
      reducer = None
       
    return distarray.create(ctx, shape, dtype,
                            combiner=combiner,
                            reducer=reducer,
                            tile_hint=tile_hint)


def ndarray(shape, 
            dtype=np.float, 
            tile_hint=None,
            combine_fn=None, 
            reduce_fn=None):
  '''
  Lazily create a new distributed array.
  :param shape:
  :param dtype:
  :param tile_hint:
  '''
  return NdArrayExpr(_shape = shape,
                     dtype = dtype,
                     tile_hint = tile_hint,
                     combine_fn = combine_fn,
                     reduce_fn = reduce_fn) 