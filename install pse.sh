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
sudo apt-get install -f zlib1g-dev libffi-dev libssl-dev openssl-dev openssl libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdm-dev libc6-dev libbz2-dev
./configure --enable-optimizations
sudo make
sudo make test
sudo make install

## install django
sudo pip3 install Django

## install mongodb
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
## debian 8 wheezy
## for debian 7 view mongodb install page
echo "deb http://repo.mongodb.org/apt/debian jessie/mongodb-org/testing main" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
sudo apt-get update
sudo apt-get install -f -y mongodb-org

# start mongodb
sudo service mongod start

## install fireworks
sudo pip3 install FireWorks
sudo pip3 install matplotlib # for visual report plots in web gui
sudo pip3 install paramiko   # for built in remote file transfer
sudo pip3 install fabric     # for daemon mode of qlaunch
sudo pip3 install requests   # for NEWT queue adapter

cd /home/$user/Desktop
echo "host: ds049170.mongolab.com
port: 49170
name: fireworks
username: test_user
password: testing123" | tee my_launchpad_testing.yaml
lpad -l my_launchpad_testing.yaml get_wflows



