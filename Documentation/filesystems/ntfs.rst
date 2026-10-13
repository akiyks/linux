.. SPDX-License-Identifier: GPL-2.0

=================================
The Linux NTFS filesystem driver
=================================


.. Table of contents

   - Overview
   - Utilities support
   - Linux file attributes
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


Linux file attributes
=====================

The driver supports lsattr(1) and chattr(1). Immutable, append-only and
nodump are stored in a private ``$LINUXFLAGS`` extended attribute within the
standard NTFS ``$EA``/``$EA_INFORMATION`` attributes. Its value is a
32-bit little-endian bitmask: bit 0 is immutable, bit 1 is append-only,
and bit 2 is nodump. Unknown bits are preserved when updating the flags;
the entry is removed when the entire value becomes zero. These settings
survive inode eviction, unmount and reboot. Direct writes to this EA
through setxattr(2) or removexattr(2) are rejected; use chattr(1) instead.

System metadata files and files protected by the ``sys_immutable`` mount
option cannot have their immutable protection cleared with chattr(1).
Protection derived solely from the mount option is not stored in the EA.
Case folding is reported according to the mount options and cannot be
configured per file. Compression and encryption are reported but cannot
be changed through chattr(1).

These Linux flags are enforced by Linux. Storing them in an NTFS EA does
not make Windows enforce immutable, append-only or nodump semantics.


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

Named-stream ioctls
===================

The named-stream ioctl interface is available regardless of
streams_interface. Open the base regular file or directory and use
NTFS_IOC_STREAM_READ and NTFS_IOC_STREAM_WRITE with a
struct ntfs_stream request. The request contains the stream name,
byte offset, and transfer length. Write requests create the stream when it
does not exist. Writes are not atomic. Error can leave partial data
changes, an extended stream size, or a newly created stream. bytes_returned
is valid only on success. Failed write does not report a completed byte
count. Use NTFS_IOC_STREAM_REMOVE to remove a stream and NTFS_IOC_LIST_STREAMS
to enumerate streams. Stream names are encoded with
the mounted NLS by default. Set NTFS_STREAM_FL_UTF16 to pass or receive
raw UTF-16LE names. These ioctls transfer stream data directly and do not
return a separate stream file descriptor.
