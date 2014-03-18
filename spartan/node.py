'''Helper for constructing trees of objects.

Provides pretty printing, equality testing, hashing and keyword initialization.
'''  
from traits.api import HasTraits
from traits.traits import CTrait

member_caches = {}

def node_str(node):
  member_strings = []
  for (k,v) in node_iteritems(node):
    if isinstance(v, list):
      v_str = ['[']
      for i, v in enumerate(v):
        v_str.append('[%d] = %s' % (i, v))
      v_str += [']']
      
      v_str = '\n'.join(v_str)
    else:
      v_str = str(v)
    member_strings.append("%s = %s" % (k, v_str))
  child_str = '  ' + ',\n'.join(member_strings)
  child_str = child_str.replace('\n', '\n  ')
  
  return "%s { \n%s \n}" % (node.node_type, child_str) 
  

def node_iteritems(node):
  for k in node.members:
    yield (k, getattr(node, k, None))


def get_members(klass):
  global member_caches
  if klass in member_caches:
    return member_caches[klass]
  
  members = []
  for k, v in klass.__dict__["__base_traits__"].iteritems():
    if isinstance(v, CTrait) and k != "trait_added" and k != "trait_modified":
      members.append(k)
  
  member_caches[klass] = members
  return members


class Node(HasTraits):
  def __init__(self, *args, **kw):
    super(Node, self).__init__(*args, **kw)
    #self.members = get_members(self.__class__)

  @property
  def members(self):
    return get_members(self.__class__)
  
  @property
  def node_type(self):
    return self.__class__.__name__

  def __str__(self):
    return node_str(self)
  
  def __repr__(self):
    return node_str(self)
