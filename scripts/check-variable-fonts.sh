#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only
# Copyright (C) Akira Yokosawa, 2024
#
# For "make pdfdocs", reports of build errors of translations.pdf started
# arriving early 2024 [1, 2].  It turned out that Fedora and openSUSE
# tumbleweed have started deploying variable-font [3] format of "Noto CJK"
# fonts [4, 5].  For PDF, a LaTeX package named xeCJK is used for CJK
# (Chinese, Japanese, Korean) pages.  xeCJK requires XeLaTeX/XeTeX, which
# does not (and likely never will) understand variable fonts for historical
# reasons.
#
# The build error happens even when both of variable- and non-variable-format
# fonts are found on the build system.  To make matters worse, Fedora enlists
# variable "Noto CJK" fonts in the requirements of langpacks-ja, -ko, -zh_CN,
# -zh_TW, etc.  Hence developers who have interest in CJK pages are more
# likely to encounter the build errors.
#
# This script is invoked from the error path of "make pdfdocs" and emits
# suggestions if variable-font files of "Noto CJK" fonts are in the list of
# fonts accessible from XeTeX.
#
# Assumption:
# File names are not modified from those of upstream Noto CJK fonts:
#     https://github.com/notofonts/noto-cjk/
#
# References:
# [1]: https://lore.kernel.org/r/8734tqsrt7.fsf@meer.lwn.net/
# [2]: https://lore.kernel.org/r/1708585803.600323099@f111.i.mail.ru/
# [3]: https://en.wikipedia.org/wiki/Variable_font
# [4]: https://fedoraproject.org/wiki/Changes/Noto_CJK_Variable_Fonts
# [5]: https://build.opensuse.org/request/show/1157217
#
#===========================================================================
# Workarounds for building translations.pdf
#===========================================================================
#
# * Denylist veriable "Noto CJK" fonts.
#   - Create $HOME/deny-vf/fontconfig/fonts.conf from template below, with
#     tweaks when necessary.  Remove leading "# ".
#     * Template:
# -----------------------------------------------------------------
# <?xml version="1.0"?>
# <!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
# <fontconfig>
# <!--
#   Ignore variable-font glob (not to break xetex)
# -->
#     <selectfont>
#         <rejectfont>
#             <!--
#                 for Fedora
#             -->
#             <glob>/usr/share/fonts/google-noto-*-cjk-vf-fonts</glob>
#             <!--
#                 for openSUSE tumbleweed
#             -->
#             <glob>/usr/share/fonts/truetype/Noto*CJK*-VF.otf</glob>
#         </rejectfont>
#     </selectfont>
# </fontconfig>
# -----------------------------------------------------------------
#
#     The denylisting is effective only for "make pdfdocs".
#
# * For skipping CJK pages in PDF
#   - Uninstall texlive-xecjk.
#     Denylisting is not needed in this case.
#
# * For printing CJK pages in PDF
#   - Need non-variable "Noto CJK" fonts.
#     * Fedora
#       - google-noto-sans-cjk-fonts
#       - google-noto-serif-cjk-fonts
#     * openSUSE tumbleweed
#       - non-variable "Noto CJK" fonts are not availabe as distro packages
#         as of April, 2024.  Fetch a set of font files from upstream Noto
#         CJK Font released at:
#           https://github.com/notofonts/noto-cjk/tree/main/Sans#super-otc
#         and at:
#           https://github.com/notofonts/noto-cjk/tree/main/Serif#super-otc
#         , then uncompress and deploy them.
#       - Remember to update fontconfig cache by running fc-cache.
#
# !!! Caution !!!
#     Uninstalling variable-font-format font packages can be dangerous.
#     They might be depended upon by other packages important for your work.
#     Among options listed above, denylisting should be less invasive, as it
#     is effective only for XeLaTeX in "make pdfdocs".

# Default per-user fontconfig path (overridden by env variable)
: ${FONTS_CONF_DENY_VF:=$HOME/deny-vf}

export XDG_CONFIG_HOME=${FONTS_CONF_DENY_VF}

vffonts=`fc-list -b | grep -iE 'file: .*noto.*cjk.*-vf' | \
	 sed -e 's/\tfile:/  file:/' -e 's/(s)$//' | sort | uniq`

if [ "x$vffonts" != "x" ] ; then
	echo '============================================================================='
	echo 'XeTeX is confused by "Noto CJK" fonts of variable-font format listed below:'
	echo "$vffonts"
	echo
	echo 'For CJK pages in PDF, those fonts need to be hidden from XeTeX by denylisted.'
	echo 'Otherwise, uninstalling texlive-xecjk should suffice.'
	echo
	echo 'For more info on denylisting, other options, and info on variable font,'
	echo 'see header comments of scripts/check-variable-fonts.sh.'
	echo '============================================================================='
fi

# As this script is invoked from Makefile's error path, always error exit
# regardless of whether any variable font is discovered or not.
exit 1
