import spartan
from spartan import core, expr, util, blob_ctx
import numpy as np
from .qr import qr

import time
from sys import stderr

def svd(A, k=None):
  """
  Stochastic SVD.

  Parameters
  ----------
  A : spartan matrix
      Array to compute the SVD on, of shape (M, N)
  k : int, optional
      Number of singular values and vectors to compute.

  The operations include matrix multiplication and QR decomposition.
  We parallelize both of them.

  Returns
  --------
  U : Spartan array of shape (M, k)
  S : numpy array of shape (k,)
  V : numpy array of shape (k, k)
  """
  if k is None:
    k = A.shape[1]

  ctx = blob_ctx.get()

  st = time.time()
  Omega = expr.randn(A.shape[1], k, tile_hint=(A.shape[1]/ctx.num_workers, k))
  r = A.shape[0] / ctx.num_workers
  Y = expr.dot(A, Omega, tile_hint=(r, k)).force()
  print >>stderr, "omega", time.time() - st
  
  st = time.time()
  Q, R = qr(Y)
  print >>stderr, "qr", time.time() - st
 


  st = time.time()
  print expr.transpose(Q).shape
  print A.shape

  B = expr.dot(expr.transpose(Q), A).force()
  print >>stderr, "QA", time.time() - st

  BTB = expr.dot(B, expr.transpose(B)).glom()
  print >>stderr, "BTB", time.time() - st
  
  S, U_ = np.linalg.eig(BTB)
  S = np.sqrt(S)

  # Sort by eigen values from large to small
  si = np.argsort(S)[::-1]
  S = S[si]
  U_ = U_[:, si]

  st = time.time()
  U = expr.dot(Q, U_).force()
  V = np.dot(np.dot(expr.transpose(B).glom(), U_), np.diag(np.ones(S.shape[0]) / S))
  print >>stderr, "UV", time.time() - st

  return U, S, V.T 
