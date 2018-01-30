#!/bin/bash

sudo yum install -y httpd
sudo yum install -y gcc openssl-devel bzip2-devel zlib-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel expat-devel

wget 'https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tar.xz'
tar -xvf Python-3.6.3.tar.xz
cd Python-3.6.3/
./configure --enable-optimizations --prefix=/usr/local --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
sudo make
sudo make altinstall
cd ..
rm Python-3.6.3.tar.xz

/usr/local/bin/python3.6 -V
/usr/local/bin/pip3.6 -V

sudo /usr/local/bin/pip3.6 install Django psycopg2 django_crontab django-cors-headers
