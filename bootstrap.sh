#!/usr/bin/env bash

# Update package list
apt-get update
apt-get -y install postgresql
apt-get -y install python3.4
apt-get -y install python-setuptools
#apt-get -y install git
apt-get -y install python3-psycopg2
apt-get -y install xfce4
#TERM=xterm-256color
#startxfce4&



if ! [ -L /var/www ]; then
  rm -rf /var/www
  ln -fs /vagrant /var/www
fi
