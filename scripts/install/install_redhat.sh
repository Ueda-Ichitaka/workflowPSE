#!/bin/bash

sudo yum install gcc openssl-devel bzip2-devel

wget 'https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tar.xz'
tar -xvf Python-3.6.3.tar.xz
cd Python-3.6.3/
./configure --enable-optimizations
sudo make altinstall
cd ..
rm Python-3.6.3.tar.xz

python3.6 -V
pip3.6 -V

sudo pip3.6 install Django
