#!/bin/bash
echo " ----------------------------
  Updating LD_LIBRARY_PATH and PATH env variables to see CUDA libraries
 ----------------------------"
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-11.7/lib64
export PATH=$PATH:/usr/local/cuda-11.7/bin
echo " ----------------------------
  Updating PATH env variables to see cudalign
 ----------------------------"
export PATH=$PATH:/home/ubuntu/MASA-CUDAlign/masa-cudalign-4.0.2.1028
echo " ----------------------------
   Installing python
 ----------------------------"
sudo apt -y update
sudo apt -y upgrade
echo " ----------------------------
   Installing pip
 ----------------------------"
sudo apt install -y python3-pip
echo " ----------------------------
   Installing scikit-fuzzy
 ----------------------------"
sudo pip install -U scikit-fuzzy
echo " ----------------------------
   Installing pycuda
 ----------------------------"
sudo pip install pycuda
echo " ----------------------------
   Installing paramiko
 ----------------------------"
sudo pip install --upgrade --ignore-installed pip setuptools
sudo pip install paramiko
echo " ----------------------------
   Installing unzip
 ----------------------------"
sudo apt install unzip -y
echo " ----------------------------
   unzip sequences
 ----------------------------"
cd sequences/
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
cd ..
echo " ----------------------------
   downloading framework
 ----------------------------"
git clone https://github.com/walissongpi/framework.git
git clone https://github.com/walissongpi/MASA-CUDAlign.git
cd MASA-CUDAlign/
unzip masa-cudalign-4.0.2.1028.zip
