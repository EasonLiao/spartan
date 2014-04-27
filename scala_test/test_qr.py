import numpy as np
from numpy import linalg
from scipy.sparse.linalg import svds
from scipy.linalg import svd, qr as sqr

import time
import math
import spartan
from spartan import expr
from spartan.examples.ssvd import qr
from spartan import util
from numpy import absolute as abs


ctx = spartan.initialize()


M = 180000 * 64 
N = 100


try:
  A = expr.rand(M, N, tile_hint=(M / ctx.num_workers, N)).force()
  print "begin"
  st = time.time()
  q, r = qr(A)
  print time.time() - st

finally:
  ctx.shutdown()

