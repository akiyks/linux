#! /bin/sh
# SPDX-License-Identifier: GPL-2.0-only
# Helper script for "pdfdocs" after running latex builder's Makefile

BUILDDIR=$1
PDFINFO_CMD=`command -v pdfinfo`

mkdir -p $BUILDDIR/pdf

errcnt=0

if [ $PDFINFO_CMD ] ; then
    if [ "x$KBUILD_VERBOSE" != "x" ] ; then
        echo "---- PDF docs build results ----"
    fi
fi

# Test generated PDF files by "pdfinfo" and copy them into /pdf/
for t in $BUILDDIR/latex/*.tex; do
    tbase=`echo $t | sed 's/\.tex//'`
    if [ -e $tbase.pdf ] ; then
        if [ $PDFINFO_CMD ] ; then
	    pdfinfo $tbase.pdf > /dev/null 2>&1
	    if [ "$?" = "0" ] ; then
		cp -f $tbase.pdf $BUILDDIR/pdf/
		if [ "x$KBUILD_VERBOSE" != "x" ] ; then
		    echo "PASS: $tbase.pdf"
		fi
	    else
		echo "FAIL: $tbase.pdf"
		errcnt=`expr $errcnt + 1`
	    fi
	else # PDFINFO_CMD
	    cp -f $tbase.pdf $BUILDDIR/pdf/
	fi
    else
	echo "FAIL (not found): $tbase.pdf"
	errcnt=`expr $errcnt + 1`
    fi
done

if test "$errcnt" -eq "0"; then
    echo "All PDF files are built."
    exit 0
else
    echo "$errcnt error(s) detected."
    exit $errcnt
fi
