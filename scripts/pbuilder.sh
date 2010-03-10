#!/bin/bash
#
# This script install and execute bootscript to test installation
# in a debian pbuilder chroot environment.
TEST_DIR=/tmp/
CLONE_NAME=t3st
CLONED_REPO_PATH=${TEST_DIR}${CLONE_NAME}
PBUILDER_SCRIPT=${TEST_DIR}pbuilder.sh

set -e

ID=$(id -u)
if [ "$ID" != "0" ]
then
	echo "You must be root to do this"
	exit 1
fi

git clone . ${CLONED_REPO_PATH}
cd ${CLONED_REPO_PATH}


cat <<EOF > ${PBUILDER_SCRIPT}
#!/bin/sh
cd ${CLONED_REPO_PATH}
apt-get update
apt-get install --assume-yes \
	git-core subversion texlive-base mercurial imagemagick ghostscript

scripts/bootstrap.sh test test@example.com password \
	localhost:8000 Test \
	.git/ \
	fixtures/initial_data.yaml
EOF

chmod +x ${PBUILDER_SCRIPT}

pbuilder --execute --bindmounts ${TEST_DIR} -- ${PBUILDER_SCRIPT}

rm -fr ${CLONED_REPO_PATH}
