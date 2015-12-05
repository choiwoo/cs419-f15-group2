#!/usr/bin/env bash

# Update package list
apt-get update
apt-get -y install postgresql
apt-get -y install python3.4
apt-get -y install python-setuptools
apt-get -y install git
apt-get -y install python3-psycopg2

# Installing peewee
git clone https://github.com/coleifer/peewee.git
cd peewee
python setup.py install

# Test

touch fooo

# Our source codes


if ! [ -L /var/www ]; then
  rm -rf /var/www
  ln -fs /vagrant /var/www
fi
