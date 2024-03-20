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

vffonts=`fc-list -b | grep -i noto | grep -i cjk | grep -F -i -e "-vf" | sort | uniq | sed -e 's/\tfile:/  file:/' | sed -e 's/(s)$//'`

if [ "x$vffonts" != "x" ] ; then
	echo "====================================================================="
	echo "Detected variable form of Noto CJK fonts incompatible with xelatex:"
	echo "$vffonts"
	echo "If you need CJK contents in PDF, remove them and install static ones."
	echo "Otherwise, get rid of texlive-xecjk."
	echo "====================================================================="
fi

exit 1
