#!/bin/bash
execute=$1
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-11.7/lib64
export PATH=$PATH:/usr/local/cuda-11.7/bin
export PATH=$PATH:/home/ubuntu/MASA-CUDAlign/masa-cudalign-4.0.2.1028
$execute
