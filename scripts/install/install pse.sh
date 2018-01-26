#!/bin/bash

## Variables
user="ueda"

sudo apt-get update
sudo apt-get upgrade

## python 3.6
## download latest python3 and unzip
cd /home/$user/Downloads
wget https://www.python.org/downloads/release/python-363/
tar -xvf Python-3.6.3.tar.xz
cd Python-3.6.3/
sudo apt-get install -f zlib1g-dev libffi-dev libssl-dev openssl-dev openssl libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdm-dev libc6-dev libbz2-dev python-pip python-dev libpq-dev postgresql postgresql-contrib
./configure --enable-optimizations
sudo make
sudo make test
sudo make install

## install django
sudo pip3.6 install Django==2.0.1 psycopg2 django_crontab





