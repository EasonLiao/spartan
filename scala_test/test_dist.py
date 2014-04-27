from distcheck import *
import distcheck
import socket

@run
def numpy_version():
  import numpy
  return numpy.__version__


@timeit
def matrix_multiply():
  import numpy as np
  a = np.random.randn(1000, 1000)
  b = np.random.randn(1000, 1000)
  np.dot(a, b)


@timeit
def sort():
  import numpy as np
  a = np.random.randn(1000, 100)
  np.argsort(a, axis=1)

if __name__ == "__main__":
  distcheck.main()
