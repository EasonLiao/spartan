from spartan import util
from spartan.util import Assert
import numpy as np

class TileExtent(object):
  '''A rectangular tile of a distributed array.
  
  These correspond (roughly) to a `slice` taken from an array
  (without any step component).
  
  Arrays are indexed from the upper-left; for an array of shape
  (sx, sy, sz): (0,0...) is the upper-left corner of an array, 
  and (sx,sy,sz...) the lower-right.
  
  Extents are represented by an upper-left corner (inclusive) and
  a lower right corner (exclusive): [ul, lr).  In addition, they
  carry the shape of the array they are a part of; this is used to
  compute global position information.
  '''
  
  @property
  def size(self):
    return np.prod(self.shape)
  
  @property
  def shape(self):
    result = self.lr_array - self.ul_array
    result[result == 0] = 1
    #util.log_info('Shape: %s', result)
    return tuple(result)
  
  @property
  def ndim(self):
    return len(self.lr)
  
  def __reduce__(self):
    return (create, (self.ul, self.lr, self.array_shape))
  
  def to_slice(self):
    return tuple([slice(ul, lr, None) for ul, lr in zip(self.ul, self.lr)])
  
  def __repr__(self):
    return 'extent(' + ','.join('%s:%s' % (a, b) for a, b in zip(self.ul, self.lr)) + ')'

  
  def __getitem__(self, idx):
    return create([self.ul[idx]], 
                  [self.lr[idx]], 
                  [self.array_shape[idx]])
                      
  def __hash__(self):
    return hash(self.ul)
    #return hash(self.ul[-2:])
    #return ravelled_pos(self.ul, self.array_shape)
    
  def __eq__(self, other):
    for i in range(len(self.ul)):
      if other.ul[i] != self.ul[i] or other.lr[i] != self.lr[i]:
        return False
    return True

  def ravelled_pos(self):
    return ravelled_pos(self.ul, self.array_shape)
  
  def to_global(self, idx, axis):
    '''Convert ``idx`` from a local offset in this tile to a global offset.'''
    if axis is not None:
      return idx + self.ul[axis]

    # first unravel idx to a local position
    local_idx = idx
    unravelled = []
    shp = self.shape
    for i in range(len(shp)):
      unravelled.append(local_idx % shp[i])
      local_idx /= shp[i]
    
    unravelled = np.array(list(reversed(unravelled)))
    unravelled += self.ul
    return ravelled_pos(unravelled, self.array_shape)

  def add_dim(self):
    return create(self.ul + (0,), 
                  self.lr + (0,), 
                  self.array_shape + (1,))

  def clone(self):
    return create(self.ul, self.lr, self.array_shape)
 
  
def create(ul, lr, array_shape):
  '''
  Create a new extent with the given coordinates and array shape.
  
  :param ul: `tuple`: 
  :param lr:
  :param array_shape:
  '''
  ex = TileExtent()
  ex.ul = tuple(ul)
  ex.lr = tuple(lr)
  
    
  assert np.all(np.array(ex.lr) >= np.array(ex.ul)),\
    'Negative extent size: (%s, %s)' % (ul, lr)
  
  if array_shape is not None:
    ex.array_shape = tuple(array_shape)
    assert np.all(np.array(ex.lr) <= np.array(array_shape)),\
      'Extent lr (%s) falls outside of the array(%s)' % (lr, array_shape)
  else:
    ex.array_shape = None
  
  # cache some values as numpy arrays for faster access
  ex.ul_array = np.asarray(ex.ul, dtype=np.int)
  ex.lr_array = np.asarray(ex.lr, dtype=np.int)
  return ex
 
def unravelled_pos(idx, array_shape): 
  '''
  Unravel ``idx`` into an index into an array of shape ``array_shape``.
  :param idx: `int`
  :param array_shape: `tuple`
  :rtype: `tuple` indexing into ``array_shape``
  '''
  
  unravelled = []
  for dim in array_shape:
    unravelled.append(idx % dim)
    idx /= dim
  util.log_info('Unravel: %s %s %s',
                idx, unravelled, array_shape)
  return tuple(unravelled)
    
def ravelled_pos(idx, array_shape):
  rpos = 0
  mul = 1
  
  for i in range(len(array_shape) - 1, -1, -1):
    rpos += mul * idx[i]
    mul *= array_shape[i]
  
  return rpos

def find_overlapping(extents, region):
  '''
  Return the extents that overlap with ``region``.   
  
  :param extents: List of extents to search over.
  :param region: `Extent` to match.
  '''
  for ex in extents:
    overlap = intersection(ex, region)
    if overlap is not None:
      yield (ex, overlap)
      

def compute_slice(base, idx):
  '''Return a new ``TileExtent`` representing ``base[idx]``
  
  :param base: `TileExtent`
  :param idx: int, slice, or tuple(slice,...)
  '''
  assert not np.isscalar(idx)
  if not isinstance(idx, tuple):
    idx = (idx,)
    
  ul = []
  lr = []
  array_shape = base.array_shape
  
  for i in range(len(base.ul)):
    if i >= len(idx):
      ul.append(base.ul[i])
      lr.append(base.lr[i])
    else:
      start, stop, step = idx[i].indices(base.shape[i])
      ul.append(base.ul[i] + start)
      lr.append(base.ul[i] + stop)
  
  return create(ul, lr, array_shape)


def offset_from(base, other):
  '''
  :param base: `TileExtent` to use as basis
  :param other: `TileExtent` into the same array.
  :rtype: A new extent using this extent as a basis, instead of (0,0,0...) 
  '''
  assert np.all(other.ul >= base.ul), (other, base)
  assert np.all(other.lr <= base.lr), (other, base)
  return create(np.array(other.ul) - np.array(base.ul), 
                np.array(other.lr) - np.array(base.ul),
                other.array_shape)



def offset_slice(base, other):
  '''
  :param base: `TileExtent` to use as basis
  :param other: `TileExtent` into the same array.
  :rtype: A slice representing the local offsets of ``other`` into this tile.
  '''
  return offset_from(base, other).to_slice()
  

def from_slice(idx, shape):
  '''
  Construct a `TileExtent` from a slice or tuple of slices.
  
  :param idx: int, slice, or tuple(slice...)
  :param shape: shape of the input array
  :rtype: `TileExtent` corresponding to ``idx``.
  '''
  if not isinstance(idx, tuple):
    idx = (idx,)
  
  if len(idx) < len(shape):
    idx = tuple(list(idx) + [slice(None, None, None) 
                             for _ in range(len(shape) - len(idx))])
    
  ul = []
  lr = []
 
  for i in range(len(shape)):
    dim = shape[i]
    slc = idx[i]
    
    if np.isscalar(slc):
      slc = int(slc)
      slc = slice(slc, slc + 1, None)
    
    if slc.start > 0: assert slc.start <= dim
    if slc.stop > 0: assert slc.stop <= dim
    
    indices = slc.indices(dim)
    ul.append(indices[0])
    lr.append(indices[1])
    
  return create(ul, lr, shape)


def intersection(a, b):
  '''
  :rtype: The intersection of the 2 extents as a `TileExtent`, 
          or None if the intersection is empty.  
  '''
  for i in range(len(a.lr)):
    if b.lr[i] < a.ul[i]: return None
    if a.lr[i] < b.ul[i]: return None
    
  Assert.eq(a.array_shape, b.array_shape)
  
  # if np.any(b.lr_array <= a.ul_array): return None
  # if np.any(a.lr_array <= b.ul_array): return None
  return create(np.maximum(b.ul_array, a.ul_array),
                np.minimum(b.lr_array, a.lr_array),
                a.array_shape)

TileExtent.intersection = intersection


def shape_for_reduction(input_shape, axis):
  '''
  Return the shape for the result of applying a reduction along ``axis`` to 
  an input of shape ``input_shape``.
  :param input_shape:
  :param axis:
  '''
  if axis == None: return ()
  input_shape = list(input_shape)
  del input_shape[axis]
  return input_shape


def shapes_match(offset, data):
  '''
  Return true if the shape of ``data`` matches the extent ``offset``. 
  :param offset:
  :param data:
  '''
  return np.all(offset.shape == data.shape)

def drop_axis(ex, axis):
  if axis is None: return create((), (), ())
  if axis < 0: axis = len(ex.ul) + axis
  
  ul = list(ex.ul)
  lr = list(ex.lr)
  shape = list(ex.array_shape)
  del ul[axis]
  del lr[axis]
  del shape[axis]
  return create(ul, lr, shape)
 
def index_for_reduction(index, axis):
  return drop_axis(index, axis)
        
def find_shape(extents):
  '''
  Given a list of extents, return the shape of the array
  necessary to fit all of them.
  :param extents:
  '''
  #util.log_info('Finding shape... %s', extents)
  shape = np.max([ex.lr for ex in extents], axis=0)
  shape[shape == 0] = 1
  return tuple(shape)