#!/bin/bash
#
# Copyright 2010 Gianluca Pacchiella <gianluca.pacchiella@ktln2.org>
#
# This script uses git mktree command to generate a subtree to include
# in the object database without track it in the official history.
TMP=.tmp-mktree

die () {
	echo $1
	exit 1
}

if [ $# -lt 3 ]
then
	die "usage: $0 prefix message tag"
fi

# TODO: check for trailing slash
PREFIX="$1"
MSG="$2"
TAG="$3"

stat ${PREFIX} 1>&2 > /dev/null || die "'${PREFIX}' doesn't exist"

echo "[+] creating tree for ${PREFIX}"

HASH=$(for f in $(ls ${PREFIX})
do
	echo  -e 100644 blob `git hash-object -w ${PREFIX}$f`"\t$f"
done | git mktree )

echo "[+] creating commit"
COMMIT_HASH=$(git commit-tree $HASH < <(echo ${MSG}))

echo "[+] creating tag"
git tag ${TAG} ${COMMIT_HASH}
