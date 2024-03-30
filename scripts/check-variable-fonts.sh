#!/bin/sh
# SPDX-License-Identifier: GPL-2.0
#
# For "make pdfdocs", reports of build errors of translations.pdf started to
# arrive since early 2024 [1, 2].  It turned out that Fedora and openSUSE
# tumbleweed has started deploying variable-font [3] format of "Noto CJK"
# fonts [4, 5].  For PDF, a LaTeX package named xeCJK is used for CJK
# (Chinese, Japanese, Korean) pages.  xeCJK requires XeLaTeX, which does not
# understand variable fonts for historical reasons.
#
# The build error happens even when both of variable- and non-variable-format
# fonts are found on the build system.  Making matters even worse, Fedora
# enlists variable-font "Noto CJK" fonts in the requirements of langpacks-ja,
# -ko, -zh_CN, _zh_TW, etc.  Hence it is likely for developers interested in
# CJK pages will encounter the build errors.
#
# This script is invoked from the error path of "make pdfdocs" and emits
# suggestions if variable-font files are found.
#
# Assumption:
# File names are not changed from those of upstream Noto CJK fonts:
#     https://github.com/notofonts/noto-cjk/
#
# References:
# [1]: https://lore.kernel.org/r/8734tqsrt7.fsf@meer.lwn.net/
# [2]: https://lore.kernel.org/r/1708585803.600323099@f111.i.mail.ru/
# [3]: https://en.wikipedia.org/wiki/Variable_font
# [4]: https://fedoraproject.org/wiki/Changes/Noto_CJK_Variable_Fonts
# [5]: https://build.opensuse.org/request/show/1157217
#
# Workarounds for building translations.pdf:
#  * Denylist veriable "Noto CJK" fonts
#    - Create $HOME/xetex/fontconfig/fonts.conf
#      * Example for Fedora
# -----------------------------------------------------------------
# <?xml version="1.0"?>
# <!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
# <fontconfig>
# <!--
#   Ignore variable-font glob (not to break xetex)
# -->
#         <selectfont>
#                 <rejectfont>
#                         <glob>/usr/share/fonts/google-noto-*-cjk-vf-fonts</glob>
#                 </rejectfont>
#         </selectfont>
# </fontconfig>
# -----------------------------------------------------------------
#        - Example for openSUSE tumbleweed
# -----------------------------------------------------------------
# <?xml version="1.0"?>
# <!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
# <fontconfig>
# <!--
#   Ignore variable-font glob (not to break xetex)
# -->
#         <selectfont>
#                 <rejectfont>
#                        <glob>/usr/share/fonts/truetype/Noto*CJK*-VF.otf</glob>
#                 </rejectfont>
#         </selectfont>
# </fontconfig>
# -----------------------------------------------------------------
#
#  * Skip CJK pages in PDF
#    - Uninstall texlive-xecjk
#
#  * Need CJK pages in PDF
#    - Install non-variable "Noto CJK" fonts
#      * Fedora
#        - google-noto-sans-cjk-fonts
#        - google-noto-serif-cjk-fonts
#      * openSUSE tumbleweed
#        - non-variable "Noto CJK" fonts are not availabe as distro packages
#          as of April, 2024.  Fetch a set of font files from upstream Noto
#          CJK Font release at:
#            https://github.com/notofonts/noto-cjk/tree/main/Sans#super-otc
#          and at:
#            https://github.com/notofonts/noto-cjk/tree/main/Serif#super-otc
#          , then unzip and manually deploy them.
#        - Don't forget to update fontconfig cache by running fc-cache.
#

vffonts=`fc-list -b | grep -iE 'file: .*noto.*cjk.*-vf' | \
	 sed -e 's/\tfile:/  file:/' -e 's/(s)$//' | sort | uniq`

if [ "x$vffonts" != "x" ] ; then
	echo "====================================================================="
	echo "Variable-font format of Noto CJK fonts listed below caused error."
	echo "$vffonts"
	echo "They are not compatible with XeTeX."
	echo
	echo "If you need CJK contents in PDF, opt-in to denylisting them."
	echo "Otherwise, get rid of texlive-xecjk."
	echo
	echo "For more info on denylisting, other options, and info on variable"
	echo "font, see header comments of scripts/check-variable-fonts.sh."
	echo "====================================================================="
fi

# As this script is invoked from Makefile's error path, always error exit
# even if no variable font is detected.
exit 1
