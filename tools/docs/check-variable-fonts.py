#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
# Copyright (C) Akira Yokosawa, 2024
#
# Ported to Python by (c) Mauro Carvalho Chehab, 2025
#
# pylint: disable=C0103

"""
Detect problematic Noto CJK variable fonts.

or more details, see lib/latex_fonts.py.
"""

import argparse
import sys

from lib.latex_fonts import LatexFontChecker

checker = LatexFontChecker()

parser=argparse.ArgumentParser(description=checker.description(),
                               formatter_class=argparse.RawTextHelpFormatter)
_=parser.parse_args()

msg = LatexFontChecker().check()
if msg:
    print(msg)

sys.exit(1)
