#! /bin/sh
BUILDDIR=$1
PDFINFO_CMD=`command -v pdfinfo`

mkdir -p $BUILDDIR/pdf

errcnt=0

if [ $PDFINFO_CMD ] ; then
    echo "---- PDF Build results ----"
fi

for t in $BUILDDIR/latex/*.tex; do
    tbase=`echo $t | sed 's/\.tex//'`
    if [ -e $tbase.pdf ] ; then
        cp -f $tbase.pdf $BUILDDIR/pdf/
        if [ $PDFINFO_CMD ] ; then
	    pdfinfo $tbase.pdf > /dev/null 2>&1
	    if [ "$?" = "0" ] ; then
		echo "PASS: $tbase.pdf"
	    else
		echo "FAIL: $tbase.pdf"
		errcnt=`expr $errcnt + 1`
	    fi
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
