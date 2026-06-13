.. SPDX-License-Identifier: GPL-2.0

=================================
The Linux NTFS filesystem driver
=================================


.. Table of contents

   - Overview
   - Utilities support
   - Supported mount options


Overview
========

NTFS is a Linux kernel filesystem driver that provides full read and write
support for NTFS volumes. It is designed for high performance, modern
kernel infrastructure (iomap, folio), and stable long-term maintenance.


Utilities support
=================

The NTFS utilities project, called ntfsprogs-plus, provides mkfs.ntfs,
fsck.ntfs, and other related tools (e.g., ntfsinfo, ntfsclone, etc.) for
creating, checking, and managing NTFS volumes. These utilities can be used
for filesystem testing with xfstests as well as for recovering corrupted
NTFS devices.

The project is available at:

  https://github.com/ntfsprogs-plus/ntfsprogs-plus


Supported mount options
=======================

The NTFS driver supports the following mount options:

.. only:: (not latex) or tblnest

  .. tabularcolumns:: >{\ttfamily}\Y{.35}\Y{.65}

  .. table::
     :class: longtable

     .. include:: ntfs-mount-opts.rst

.. only:: latex and (not tblnest)

  .. literalinclude:: ntfs-mount-opts.rst
     :tab-width: 8
