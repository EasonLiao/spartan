import numpy as np
import spartan
from spartan import expr
from numpy import linalg
from scipy.sparse.linalg import svds
import time
from spartan.examples.sklearn.neighbors import NearestNeighbors as KNN

ctx = spartan.initialize()

DIM = 64 
SAMPLES_PER_WORKER = 150000
SAMPLES = SAMPLES_PER_WORKER * 64 

Q_SAMPLES = 10 

try:
  print SAMPLES
  X = expr.randn(SAMPLES, DIM, tile_hint=(SAMPLES/ctx.num_workers, DIM)).force()
  Q = np.random.randn(Q_SAMPLES, DIM)
  
  st = time.time()
  dist, ind = KNN(algorithm="kd_tree").fit(X).kneighbors(Q, 5)
  print time.time() - st

finally:
  ctx.shutdown()

