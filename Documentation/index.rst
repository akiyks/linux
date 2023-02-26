.. SPDX-License-Identifier: GPL-2.0

.. _linux_doc:

==============================
The Linux Kernel documentation
==============================

This is the top level of the kernel's documentation tree.  Kernel
documentation, like the kernel itself, is very much a work in progress;
that is especially true as we work to integrate our many scattered
documents into a coherent whole.  Please note that improvements to the
documentation are welcome; join the linux-doc list at vger.kernel.org if
you want to help out.


Select documents
================

Here are lists of essential documentation.
For the full table of contents, see `Full TOC tree`_ below.

.. include:: select-docs-list.rst


.. _full_toc_tree:

Full TOC tree
=============

.. toctree::
   :maxdepth: 1

   select-docs

   process/index
   maintainer/index

   core-api/index
   driver-api/index
   subsystem-apis
   Locking in the kernel <locking/index>

   doc-guide/index
   dev-tools/index
   kernel-hacking/index
   trace/index
   fault-injection/index
   livepatch/index
   rust/index

   admin-guide/index
   The kernel build system <kbuild/index>
   User-space tools <tools/index>
   userspace-api/index

   firmware-guide/index
   devicetree/index

   arch

   staging/index

   translations/index
