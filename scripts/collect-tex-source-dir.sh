#! /bin/sh
BUILDDIR=$1
shift
SPHINXDIRS=$@

mkdir -p $BUILDDIR/latex

for sub in $SPHINXDIRS; do
    cp -f $BUILDDIR/$sub/latex/* $BUILDDIR/latex/
done
