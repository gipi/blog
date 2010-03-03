#!/bin/bash
#
# This script is intended for final deployment once the source
# code is in the correct location.
#
# Steps
#
#     1. create virtualenv and activate it
#     2. install by pip dependencies
#     3. create local_settings.py
#     4. syncdb
#     5. load initial data
ENV_ROOT=env/
SECRET_KEY_CMD="python -c 'import random; print \"\".join([random.choice(\"abcdefghijklmnopqrstuvwxyz0123456789\!@#$%^&*(-_=+)\") for i in range(50)])'"

message () {
	echo -e "$1"
}

usage () {
	echo "usage: $0 name mail_address password site_URL site_name [ fixture1 fixture2 ... ]"
}

if [ $# -lt 5 ]
then
	usage
	exit 1
fi

NAME=$1
EMAIL=$2
PASSWORD=$3
SITE_URL=$4
SITE_NAME=$5

# exec 2> /tmp/installation.log

if [ -e "env/" ]
then
	message "'env/' directory already exists"
	exit 1
fi

# INSTALL DEPENDENCIES
export PYTHONPATH=
virtualenv --no-site-packages ${ENV_ROOT}
source ${ENV_ROOT}bin/activate

easy_install pip 
pip install -r scripts/dependencies.txt

# CREATE local_settings.py
message "[local settings]"
cat <<EOF >> local_settings.py
# `date`
SECRET_KEY = "`eval ${SECRET_KEY_CMD}`"

EOF

# CREATE version.py
VERSION=`git describe --tags`
echo SNIPPY_GIT_VERSION=\'${VERSION}\' > version.py

# CREATE NECESSARY DIRS
mkdir media/TeX media/fonts media/uploads
# TESTS
python manage.py test

# CREATE DATABASE
python manage.py syncdb

# Site and User initializated
cat <<EOF | python manage.py shell

from django.contrib.sites.models import Site

site = Site.objects.get(pk=1)
site.domain = "${SITE_URL}"
site.name = "${SITE_NAME}"
site.save()

from django.contrib.auth.models import User

User.objects.create_user("${NAME}", "${EMAIL}", password="${PASSWORD}")

EOF

# LOAD fixtures
# first shift the args from commandline
shift 5
echo "loading fixtures: $@"

python manage.py loaddata $@

echo '
Remember to set variable in local_settings.py to reflect
database which you have in the server.

Remember also to deploy files not included into the repository.
'
