#!/bin/bash
arch=$1
echo " ----------------------------
  Updating LD_LIBRARY_PATH and PATH env variables to see CUDA libraries
 ----------------------------"
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-11.7/lib64
export PATH=$PATH:/usr/local/cuda-11.7/bin
pip install gputil
echo " ----------------------------
  Downloading MASA-CUDAlign...
 ----------------------------"
git clone https://github.com/walissongpi/MASA-CUDAlign.git
cd MASA-CUDAlign
unzip masa-cudalign-4.0.2.1028.zip
cd masa-cudalign-4.0.2.1028
make clean
./configure -with-cuda-arch=$arch
make
cd ..
cd ..
echo " ----------------------------
  Updating PATH env variables to see cudalign
 ----------------------------"
export PATH=$PATH:/home/ubuntu/MASA-CUDAlign/masa-cudalign-4.0.2.1028
echo " ----------------------------
   Downloading sequences
 ----------------------------"
git clone https://github.com/walissongpi/sequences.git
echo " ----------------------------
   unzip sequences
 ----------------------------"
cd sequences
unzip 2k.zip
unzip 10k.zip
unzip 18k.zip
unzip 30k.zip
unzip 200k.zip
unzip 1-3M.zip
unzip 2-5M.zip
unzip 3-7M.zip
unzip 4-10M.zip
unzip 5-23M.zip
unzip 6-47M.zip
unzip chr21.zip
unzip chr22.zip
unzip chrY.zip
unzip chr19-1.zip
unzip chr19-2.zip
cd ..
echo " ----------------------------
   downloading framework
 ----------------------------"
git clone https://github.com/walissongpi/framework.git
