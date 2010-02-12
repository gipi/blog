#!/bin/bash
#
# This script dumps the content of database and save it in a (remote?)
# git repository.
#
# Needs a .backuprc file where set the following variables
#
#	GIT_OBJ_DB_PATH
cd $(dirname $0)

# activate the virtualenv
export PYTHONPATH=
source env/bin/activate

if [ ! -e .backuprc ]
then
	echo "Could not found .backuprc file"
	exit 1
fi

# read settings
. ./.backuprc

# check the variable
if [ "${GIT_OBJ_DB_PATH}" == "" ]
then
	echo "Do you have set GIT_OBJ_DB_PATH variable?"
	exit 1
fi

TMP_DIR=$(mktemp -d)

# exit on failure
set -e

# create the repository in case it doesn't exist
if [ ! -e ${GIT_OBJ_DB_PATH} ]
then
	mkdir ${GIT_OBJ_DB_PATH}
	( cd ${GIT_OBJ_DB_PATH} && git init --bare )
fi

cat <<EOF | while read line; do python ../manage.py dumpdata --format yaml --indent 2 ${line} > ${TMP_DIR}/${line}.yaml ;done
yadb
comments
EOF

export GIT_DIR=${GIT_OBJ_DB_PATH}
export GIT_WORK_TREE=${TMP_DIR}
git add .
if git status; then git commit -m '[backup]';fi

rm -vfr ${TMP_DIR}
