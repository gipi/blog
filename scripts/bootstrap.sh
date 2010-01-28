#!/bin/bash
#
# This script is intended for final deployment once the source
# code is in the correct location.
ENV_ROOT=env/
SECRET_KEY_CMD="python -c 'import random; print \"\".join([random.choice(\"abcdefghijklmnopqrstuvwxyz0123456789\!@#$%^&*(-_=+)\") for i in range(50)])'"

message () {
	echo -e "$1"
}

# exec 2> /tmp/installation.log

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

# CREATE NECESSARY DIRS
mkdir media/TeX media/fonts media/uploads
# TESTS
python manage.py test snippet

# LOAD fixtures
python manage.py loaddata 
