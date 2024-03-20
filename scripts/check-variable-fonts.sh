#!/bin/sh
#
# For "make pdfdocs", recent trend of employing variable-font type of
# "Noto Sans CJK" and "Noto Serif CJK" fonts seen in distros such as
# Fedora and openSUSE tumbelweed breaks xelatex, which does not understand
# variable fonts.
#
# It is hard to distinguish variable font from static font in the preamble
# LaTeX source code, this script searches .log file for font warnings
# indicating existence of variable font.

# arg

builddir=$1

vffonts=`fc-list -b | grep Noto | grep CJK | grep -F -e "-VF" | sort | uniq | sed -e 's/\tfile:/  file:/' | sed -e 's/(s)$//'`

if [ "x$vffonts" != "x" ] ; then
	echo "======================================================="
	echo "Detected variable type of Noto CJK fonts:"
	echo "$vffonts"
	echo "Please remove them and install static ones if you need"
	echo "CJK contents rendered."
	echo "Otherwise, get rid of texlive-xecjk."
	echo "======================================================="
fi

exit 255
