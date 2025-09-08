#! /bin/sh
# SPDX-License-Identifier: GPL-2.0-only
# Helper script for "pdfdocs" before running latex builder's Makefile

BUILDDIR=$1
shift
SPHINXDIRS=$@

mkdir -p $BUILDDIR/latex

# Collect latex sources for each SPHINXDIRS in top level /latex/.

for sub in $SPHINXDIRS; do
    cp -f $BUILDDIR/$sub/latex/* $BUILDDIR/latex/
done
