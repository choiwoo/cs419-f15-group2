#!/usr/bin/env bash

# Edt the following to change the name of the database user and password
DB_USER=guest01
DB_PASS=pass01

# Edit the following to change the name of the database that is created (username is default)
DB_NAME=$DB_USER

# Update package list
apt-get update
apt-get -y install postgresql
apt-get -y install python3.4
apt-get -y install python-setuptools
#apt-get -y install git
apt-get -y install python3-psycopg2
apt-get -y install xfce4

# Postgres set up
# Creates user, password and a sample database
cat << EOF | su - postgres -c psql
-- Create the database user:
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';

-- Create the database:
CREATE DATABASE $DB_NAME WITH OWNER=$DB_USER
                                  LC_COLLATE='en_US.utf8'
                                  LC_CTYPE='en_US.utf8'
                                  ENCODING='UTF8'
                                  TEMPLATE=template0;
EOF

echo "USER= $DB_USER"
echo "PASSWORD = $DB_PASS"
echo "DATABASE = $DB_NAME"


# Copy directory to home directory
cp -r /vagrant/cs419-f15-group2/* /home/vagrant



if ! [ -L /var/www ]; then
  rm -rf /var/www
  ln -fs /vagrant /var/www
fi
