#!/bin/bash

## Variables
user="ueda"
pywps_from_source="0"
pywps_install_dir="/home/$user"


echo "Set up variables now?"
read setup



if [[ $setup =~ ^[Yy]$ ]]
then
	read -p 'Username: ' user
	read -p 'Install Python 3.6: ' python
	read -p 'Install PyWPS?: ' pywps
	read -p 'PyWPS install dir: ' pywps_dir
	
fi

echo $user
echo $python
echo $pywps
echo $pswps_dir

sudo apt-get update
sudo apt-get upgrade

## python 3.6
## download latest python3 and unzip
if [ $python3 = "1" ]
then

	cd /home/$user/Downloads
	wget https://www.python.org/downloads/release/python-363/
	tar -xvf Python-3.6.3.tar.xz
	cd Python-3.6.3/
	sudo apt-get install -f apache2 zlib1g-dev libffi-dev libssl-dev openssl-dev openssl libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdm-dev libc6-dev libbz2-dev python-pip python-dev libpq-dev postgresql postgresql-contrib libapache2-mod-wsgi-py3
	./configure --enable-optimizations
	sudo make
	sudo make test
	sudo make install
	cd ..
	rm Python-3.6.3.tar.xz
	echo	
	echo "Done installing Python"
fi

## install django and other dependencies
cd /home/$user/
sudo pip3.6 install Django==2.0.1 psycopg2==2.7.3.2 django_crontab==0.7.1 docutils==0.14 pywps==4.0.0 django-cors-headers==2.1.0 certifi==2017.11.5 cffi==1.11.2 chardet==3.0.4 click==6.7 cryptography==2.1.3 cycler==0.10.0 Flask==0.12.2 idna==2.6 itsdangerous==0.24 Jinja2==2.10 jsonschema==2.6.0 lxml==4.1.1 MarkupSafe==1.0 matplotlib==2.1.0 numpy==1.13.3 OWSLib==0.15.0 pyasn1==0.3.7 pycparser==2.18 pyparsing==2.2.0
python-dateutil==2.6.1 pytz==2017.3 requests==2.18.4 six==1.11.0 SQLAlchemy==1.1.15 urllib3==1.22 Werkzeug==0.12.2	

## install pywps
if [ $pywps_from_source = "1" ]
then
	cd $pywps_install_dir
	sudo apt-get install -f git python-gdal
	sudo pip3.6 install -e git+https://github.com/geopython/pywps.git@master#egg=pywps-dev
	git clone https://github.com/geopython/pywps-demo.git
	cd src/pywps/
	sudo pip3.6 install -r requirements.txt
fi
## pip install requirements.txt



