from scipy.spatial import distance
import numpy as np
from spartan import expr
import spartan
from spartan.examples.cf import * #ItemBasedRecommender
import time
import scipy.sparse as sp

ctx = spartan.initialize()

M = 4000 
N = int(16000 * np.sqrt(ctx.num_workers))
#N = int(12000 * np.sqrt(9))

"""
M = 80000 
N = 10000 * 2 
"""

try:
  data = expr.sparse_rand((M, N), dtype=np.float64, density=0.01, format="csr", tile_hint=(M, N/ctx.num_workers)).force() 
  print "finish array"

  model = ItemBasedRecommender(data, 10)
  st = time.time()
  model.precompute()
  print time.time() - st
finally:
  ctx.shutdown()
