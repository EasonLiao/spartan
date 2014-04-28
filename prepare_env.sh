#sudo apt-get install libatlas-base-dev;
for machine in `cat ~/machines`;
do
  echo "fix $machine"
  expect -f install.expect $machine;
done

export LAPACK=/usr/lib/lapack/liblapack.so
export ATLAS=/usr/lib/atlas-base/libatlas.so
export BLAS=/usr/lib/libblas.so

#pip install numpy --user -I;
#pip install scipy --user -I;
