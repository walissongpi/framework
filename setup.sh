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

if [ -f "flag" ]; then
    echo "The script file has alredy been run. Leaving..."
    exit 0
fi

echo " ----------------------------
   Installing python
 ----------------------------"
sudo apt install python -y

echo " ----------------------------
   Installing scikit-fuzzy
 ----------------------------"
sudo pip install -U scikit-fuzzy -y
echo " ----------------------------
   Installing pycuda
 ----------------------------"
sudo pip install pycuda -y

echo " ----------------------------
   Installing paramiko
 ----------------------------"
sudo pip install --upgrade --ignore-installed pip setuptools -y
sudo pip install paramiko -y

echo " ----------------------------
   Installing unzip
 ----------------------------"
sudo apt install unzip -y

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
cd ..

echo " ----------------------------
   downloading framework
 ----------------------------" 
git clone https://github.com/walissongpi/framework.git
echo "flag" > ${HOME}/flag
