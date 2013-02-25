#!/bin/bash
#
# This script is intended for final deployment once the source
# code is in the correct location. It has to be executed on the
# root directory of your django project.
#
# Steps
#
#     1. create virtualenv and activate it
#     2. install by pip dependencies
#     3. create local_settings.py
#     4. syncdb
#     5. load initial data

source $(dirname $0)/lib-shell.sh

ENV_ROOT=env/
BOOTSTRAP_STATE='start'
COUNTER=1

print_bootstrap_state () {
	fail_message "exit on '${BOOTSTRAP_STATE}'"
	exit 1
}

exec 2>&1
> .error.log

# on first error exit
set -e

state_message () {
	BOOTSTRAP_STATE="$1"
	echo -n "Step ${COUNTER}: "
	ok_message "$1"
	COUNTER=$((${COUNTER}+1))
}

usage () {
	echo "usage: $0 \
name mail_address password \
site_URL site_name \
git_bare_repo_path.git \
[ fixture1 fixture2 ... ]"
}

# exec 2> /tmp/installation.log
check_and_create_virtualenv () {
	state_message "installing virtualenv"
	if [ -d virtualenv ]
	then
		warning_message "'virtualenv/' already present"
	else
		# download and install
		hg clone http://bitbucket.org/ianb/virtualenv/
		( cd virtualenv ; python2.5 setup.py install --root .. )
	fi
}

check_and_do_env () {
	state_message "create new virtualenv and activate it"
	if [ -d "env/" ]
	then
		warning_message "*** 'env/' directory already exists"
	else
		PYTHONPATH=usr/lib/python2.5/site-packages/ usr/bin/virtualenv \
			--no-site-packages ${ENV_ROOT}
	fi
}

if [ $# -lt 6 ]
then
	usage
	exit 1
fi

NAME=$1
EMAIL=$2
PASSWORD=$3
SITE_URL=$4
SITE_NAME=$5

# set object database path
export GIT_DIR="$6"
if [ ! -d "${GIT_DIR}" ]
then
	echo "${GIT_DIR} doesn't exist"
	echo "you are in $PWD"
	exit 1
fi

# let me know where you are exited
trap print_bootstrap_state 0

check_and_create_virtualenv
check_and_do_env
export PYTHONPATH=
source ${ENV_ROOT}bin/activate

SECRET_KEY_CMD="python -c 'import random; print \"\".join([random.choice(\"abcdefghijklmnopqrstuvwxyz0123456789\!@#$%^&*(-_=+)\") for i in range(50)])'"


# INSTALL DEPENDENCIES
state_message "install pip and site dependencies"
easy_install pip 
pip install -r scripts/dependencies.txt

# CREATE local_settings.py
state_message "local settings"
cat <<EOF >> local_settings.py
# `date`
SECRET_KEY = "`eval ${SECRET_KEY_CMD}`"

EOF

# CREATE version.py
VERSION=`git describe --tags`
echo SNIPPY_GIT_VERSION=\'${VERSION}\' > version.py

# CREATE NECESSARY DIRS
state_message "creating media subdirectories"
mkdir --parents media/TeX media/fonts media/uploads
# TESTS
state_message "tests"
python manage.py test

# CREATE DATABASE
state_message "create database"
python manage.py syncdb

# Site and User initializated
state_message "create user and site into database"
SHA1_PSW=$( echo -n ${PASSWORD} | sha1sum )
SALT=$(date | sha1sum | head -c 5)
cat <<EOF > /tmp/miao.json
[
  {
    "model": "sites.site",
    "pk": 1,
    "fields": {
      "domain": "${SITE_URL}",
      "name": "${SITE_NAME}"
    }
  },
  {
    "model": "auth.user",
    "pk": 1,
    "fields": {
      "username": "${NAME}",
      "email": "${EMAIL}",
      "password": "sha1\$${SALT}${SHA1_PSW}"
    }
  }
]
EOF

python manage.py loaddata /tmp/miao.json

# LOAD fixtures
# first shift the args from commandline
shift 6
state_message "loading fixtures: $@"
python manage.py loaddata $@

# it's all right, reset trap
trap - 0

# little reminder
echo '
Remember to

  0. delete/drop previous database if exists

  1. set variable in local_settings.py to reflect database, smtp and
     other settings that you have in the server.

  2. deploy files not included into the repository using "scripts/dumptree.sh".

  3. eventually copy the htaccess and run.fcgi file

  4. set scripts/.backuprc and cron job to scripts/backup.sh

  5. eventually create superuser

  6. ln -s /path/to/django/contrib/admin/media admin_media

  after all try
  
  	$ PAH_INFO=/blog/ ./run.fcgi
'