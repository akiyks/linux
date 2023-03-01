.. SPDX-License-Identifier: GPL-2.0

===========================================
The Linux Kernel documentation (quick refs)
===========================================

This is a copy of the kernel's documentation tree's :doc:`top page <index>`.
Kernel documentation, like the kernel itself, is very much a work in progress;
that is especially true as we work to integrate our many scattered
documents into a coherent whole.  Please note that improvements to the
documentation are welcome; join the linux-doc list at vger.kernel.org if
you want to help out.

Working with the development community
======================================

The essential guides for interacting with the kernel's development
community and getting your work upstream.

* process/development-process.rst
* process/submitting-patches.rst
* :doc:`Code of conduct <process/code-of-conduct>`
* maintainer/index.rst
* :doc:`All development-process docs <process/index>`


Internal API manuals
====================

Manuals for use by developers working to interface with the rest of the
kernel.

* core-api/index.rst
* driver-api/index.rst
* subsystem-apis.rst
* :doc:`Locking in the kernel <locking/index>`

Development tools and processes
===============================

Various other manuals with useful information for all kernel developers.

* process/license-rules.rst
* doc-guide/index.rst
* dev-tools/index.rst
* dev-tools/testing-overview.rst
* kernel-hacking/index.rst
* trace/index.rst
* fault-injection/index.rst
* livepatch/index.rst
* rust/index.rst


User-oriented documentation
===========================

The following manuals are written for *users* of the kernel — those who are
trying to get it to work optimally on a given system and application
developers seeking information on the kernel's user-space APIs.

* admin-guide/index.rst
* :doc:`The kernel build system <kbuild/index>`
* admin-guide/reporting-issues.rst
* :doc:`User-space tools <tools/index>`
* userspace-api/index.rst

See also: the `Linux man pages <https://www.kernel.org/doc/man-pages/>`_,
which are kept separately from the kernel's own documentation.

Firmware-related documentation
==============================
The following holds information on the kernel's expectations regarding the
platform firmwares.

* firmware-guide/index.rst
* devicetree/index.rst


Architecture-specific documentation
===================================

* arch.rst

  - arc/index.rst
  - arm/index.rst
  - arm64/index.rst
  - ia64/index.rst
  - loongarch/index.rst
  - m68k/index.rst
  - mips/index.rst
  - nios2/index.rst
  - openrisc/index.rst
  - parisc/index.rst
  - powerpc/index.rst
  - riscv/index.rst
  - s390/index.rst
  - sh/index.rst
  - sparc/index.rst
  - x86/index.rst
  - xtensa/index.rst


Other documentation
===================

There are several unsorted documents that don't seem to fit on other parts
of the documentation body, or may require some adjustments and/or conversion
to ReStructured Text format, or are simply too old.

* staging/index.rst


Translations
============

* translations/index.rst

  - translations/zh_CN/index.rst
  - translations/zh_TW/index.rst
  - translations/it_IT/index.rst
  - translations/ko_KR/index.rst
  - translations/ja_JP/index.rst
  - translations/sp_SP/index.rst
  - :ref:`translations_disclaimer`

Indices and tables
==================

* :ref:`genindex`
