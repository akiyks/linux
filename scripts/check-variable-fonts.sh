#!/bin/sh
# SPDX-License-Identifier: GPL-2.0
#
# For "make pdfdocs", recent trend of deploying variable type of
# "Noto Sans CJK" and "Noto Serif CJK" fonts breaks xelatex, which does
# not understand variable fonts.
#
# It is hard to distinguish variable fonts from static ones in the preamble
# of LaTeX source code.  Instead, this script is invoked in the error path
# of "make pdfdocs" and emit suggestions if such font files are found.
#
# Assumption:
# File names are not changed from those of upstream Noto CJK fonts:
#     https://github.com/notofonts/noto-cjk/

vffonts=`fc-list -b | grep Noto | grep CJK | grep -F -e "-VF" | sort | uniq | sed -e 's/\tfile:/  file:/' | sed -e 's/(s)$//'`

if [ "x$vffonts" != "x" ] ; then
	echo "=========================================================="
	echo "Detected variable type of Noto CJK fonts:"
	echo "$vffonts"
	echo "If you need CJK contents printed, remove them and install"
	echo "static ones.  Otherwise, get rid of texlive-xecjk."
	echo "=========================================================="
fi

exit 1
