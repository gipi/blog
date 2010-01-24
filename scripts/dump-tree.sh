#!/bin/bash
#
# Copyright 2010 Gianluca Pacchiella <gianluca.pacchiella@ktln2.org>
#
# Script which dump files pointed by tag created
# with 'scripts/generate-tree.sh'.

die () {
	echo "$1"
	exit 1
}

usage () {
	echo "usage: $0 sha1 prefix"
}

if [ $# -lt 2 ]
then
	usage
	die 
fi

SHA1=$1
PREFIX=$2

while read stat type hash name
do
	git cat-file -p ${hash} > ${PREFIX}/${name}
done < <(git ls-tree ${SHA1})
