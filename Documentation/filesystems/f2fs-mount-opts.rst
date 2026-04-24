======================== ============================================================
background_gc=%s	 Turn on/off cleaning operations, namely garbage
			 collection, triggered in background when I/O subsystem is
			 idle. If background_gc=on, it will turn on the garbage
			 collection and if background_gc=off, garbage collection
			 will be turned off. If background_gc=sync, it will turn
			 on synchronous garbage collection running in background.
			 Default value for this option is on. So garbage
			 collection is on by default.
gc_merge		 When background_gc is on, this option can be enabled to
			 let background GC thread to handle foreground GC requests,
			 it can eliminate the sluggish issue caused by slow foreground
			 GC operation when GC is triggered from a process with limited
			 I/O and CPU resources.
nogc_merge		 Disable GC merge feature.
disable_roll_forward	 Disable the roll-forward recovery routine
norecovery		 Disable the roll-forward recovery routine, mounted read-
			 only (i.e., -o ro,disable_roll_forward)
discard/nodiscard	 Enable/disable real-time discard in f2fs, if discard is
			 enabled, f2fs will issue discard/TRIM commands when a
			 segment is cleaned.
heap/no_heap		 Deprecated.
nouser_xattr		 Disable Extended User Attributes. Note: xattr is enabled
			 by default if CONFIG_F2FS_FS_XATTR is selected.
noacl			 Disable POSIX Access Control List. Note: acl is enabled
			 by default if CONFIG_F2FS_FS_POSIX_ACL is selected.
active_logs=%u		 Support configuring the number of active logs. In the
			 current design, f2fs supports only 2, 4, and 6 logs.
			 Default number is 6.
disable_ext_identify	 Disable the extension list configured by mkfs, so f2fs
			 is not aware of cold files such as media files.
inline_xattr		 Enable the inline xattrs feature.
noinline_xattr		 Disable the inline xattrs feature.
inline_xattr_size=%u	 Support configuring inline xattr size, it depends on
			 flexible inline xattr feature.
inline_data		 Enable the inline data feature: Newly created small (<~3.4k)
			 files can be written into inode block.
inline_dentry		 Enable the inline dir feature: data in newly created
			 directory entries can be written into inode block. The
			 space of inode block which is used to store inline
			 dentries is limited to ~3.4k.
noinline_dentry		 Disable the inline dentry feature.
flush_merge		 Merge concurrent cache_flush commands as much as possible
			 to eliminate redundant command issues. If the underlying
			 device handles the cache_flush command relatively slowly,
			 recommend to enable this option.
nobarrier		 This option can be used if underlying storage guarantees
			 its cached data should be written to the novolatile area.
			 If this option is set, no cache_flush commands are issued
			 but f2fs still guarantees the write ordering of all the
			 data writes.
barrier			 If this option is set, cache_flush commands are allowed to be
			 issued.
fastboot		 This option is used when a system wants to reduce mount
			 time as much as possible, even though normal performance
			 can be sacrificed.
extent_cache		 Enable an extent cache based on rb-tree, it can cache
			 as many as extent which map between contiguous logical
			 address and physical address per inode, resulting in
			 increasing the cache hit ratio. Set by default.
noextent_cache		 Disable an extent cache based on rb-tree explicitly, see
			 the above extent_cache mount option.
noinline_data		 Disable the inline data feature, inline data feature is
			 enabled by default.
data_flush		 Enable data flushing before checkpoint in order to
			 persist data of regular and symlink.
reserve_root=%d		 Support configuring reserved space which is used for
			 allocation from a privileged user with specified uid or
			 gid, unit: 4KB, the default limit is 12.5% of user blocks.
reserve_node=%d		 Support configuring reserved nodes which are used for
			 allocation from a privileged user with specified uid or
			 gid, the default limit is 12.5% of all nodes.
resuid=%d		 The user ID which may use the reserved blocks and nodes.
resgid=%d		 The group ID which may use the reserved blocks and nodes.
fault_injection=%d	 Enable fault injection in all supported types with
			 specified injection rate.
fault_type=%d		 Support configuring fault injection type, should be
			 enabled with fault_injection option, fault type value
			 is shown below, it supports single or combined type.

			 ===========================      ==========
			 Type_Name                        Type_Value
			 ===========================      ==========
			 FAULT_KMALLOC                    0x00000001
			 FAULT_KVMALLOC                   0x00000002
			 FAULT_PAGE_ALLOC                 0x00000004
			 FAULT_PAGE_GET                   0x00000008
			 FAULT_ALLOC_BIO                  0x00000010 (obsolete)
			 FAULT_ALLOC_NID                  0x00000020
			 FAULT_ORPHAN                     0x00000040
			 FAULT_BLOCK                      0x00000080
			 FAULT_DIR_DEPTH                  0x00000100
			 FAULT_EVICT_INODE                0x00000200
			 FAULT_TRUNCATE                   0x00000400
			 FAULT_READ_IO                    0x00000800
			 FAULT_CHECKPOINT                 0x00001000
			 FAULT_DISCARD                    0x00002000 (obsolete)
			 FAULT_WRITE_IO                   0x00004000
			 FAULT_SLAB_ALLOC                 0x00008000
			 FAULT_DQUOT_INIT                 0x00010000
			 FAULT_LOCK_OP                    0x00020000
			 FAULT_BLKADDR_VALIDITY           0x00040000
			 FAULT_BLKADDR_CONSISTENCE        0x00080000
			 FAULT_NO_SEGMENT                 0x00100000
			 FAULT_INCONSISTENT_FOOTER        0x00200000
			 FAULT_ATOMIC_TIMEOUT             0x00400000 (1000ms)
			 FAULT_VMALLOC                    0x00800000
			 FAULT_LOCK_TIMEOUT               0x01000000 (1000ms)
			 FAULT_SKIP_WRITE                 0x02000000
			 ===========================      ==========
mode=%s			 Control block allocation mode which supports "adaptive"
			 and "lfs". In "lfs" mode, there should be no random
			 writes towards main area.
			 "fragment:segment" and "fragment:block" are newly added here.
			 These are developer options for experiments to simulate filesystem
			 fragmentation/after-GC situation itself. The developers use these
			 modes to understand filesystem fragmentation/after-GC condition well,
			 and eventually get some insights to handle them better.
			 In "fragment:segment", f2fs allocates a new segment in random
			 position. With this, we can simulate the after-GC condition.
			 In "fragment:block", we can scatter block allocation with
			 "max_fragment_chunk" and "max_fragment_hole" sysfs nodes.
			 We added some randomness to both chunk and hole size to make
			 it close to realistic IO pattern. So, in this mode, f2fs will allocate
			 1..<max_fragment_chunk> blocks in a chunk and make a hole in the
			 length of 1..<max_fragment_hole> by turns. With this, the newly
			 allocated blocks will be scattered throughout the whole partition.
			 Note that "fragment:block" implicitly enables "fragment:segment"
			 option for more randomness.
			 Please, use these options for your experiments and we strongly
			 recommend to re-format the filesystem after using these options.
usrquota		 Enable plain user disk quota accounting.
grpquota		 Enable plain group disk quota accounting.
prjquota		 Enable plain project quota accounting.
usrjquota=<file>	 Appoint specified file and type during mount, so that quota
grpjquota=<file>	 information can be properly updated during recovery flow,
prjjquota=<file>	 <quota file>: must be in root directory;
jqfmt=<quota type>	 <quota type>: [vfsold,vfsv0,vfsv1].
usrjquota=		 Turn off user journalled quota.
grpjquota=		 Turn off group journalled quota.
prjjquota=		 Turn off project journalled quota.
quota			 Enable plain user disk quota accounting.
noquota			 Disable all plain disk quota option.
alloc_mode=%s		 Adjust block allocation policy, which supports "reuse"
			 and "default".
fsync_mode=%s		 Control the policy of fsync. Currently supports "posix",
			 "strict", and "nobarrier". In "posix" mode, which is
			 default, fsync will follow POSIX semantics and does a
			 light operation to improve the filesystem performance.
			 In "strict" mode, fsync will be heavy and behaves in line
			 with xfs, ext4 and btrfs, where xfstest generic/342 will
			 pass, but the performance will regress. "nobarrier" is
			 based on "posix", but doesn't issue flush command for
			 non-atomic files likewise "nobarrier" mount option.
test_dummy_encryption
test_dummy_encryption=%s
			 Enable dummy encryption, which provides a fake fscrypt
			 context. The fake fscrypt context is used by xfstests.
			 The argument may be either "v1" or "v2", in order to
			 select the corresponding fscrypt policy version.
checkpoint=%s[:%u[%]]	 Set to "disable" to turn off checkpointing. Set to "enable"
			 to re-enable checkpointing. Is enabled by default. While
			 disabled, any unmounting or unexpected shutdowns will cause
			 the filesystem contents to appear as they did when the
			 filesystem was mounted with that option.
			 While mounting with checkpoint=disable, the filesystem must
			 run garbage collection to ensure that all available space can
			 be used. If this takes too much time, the mount may return
			 EAGAIN. You may optionally add a value to indicate how much
			 of the disk you would be willing to temporarily give up to
			 avoid additional garbage collection. This can be given as a
			 number of blocks, or as a percent. For instance, mounting
			 with checkpoint=disable:100% would always succeed, but it may
			 hide up to all remaining free space. The actual space that
			 would be unusable can be viewed at /sys/fs/f2fs/<disk>/unusable
			 This space is reclaimed once checkpoint=enable.
checkpoint_merge	 When checkpoint is enabled, this can be used to create a kernel
			 daemon and make it to merge concurrent checkpoint requests as
			 much as possible to eliminate redundant checkpoint issues. Plus,
			 we can eliminate the sluggish issue caused by slow checkpoint
			 operation when the checkpoint is done in a process context in
			 a cgroup having low i/o budget and cpu shares. To make this
			 do better, we set the default i/o priority of the kernel daemon
			 to "3", to give one higher priority than other kernel threads.
			 This is the same way to give a I/O priority to the jbd2
			 journaling thread of ext4 filesystem.
nocheckpoint_merge	 Disable checkpoint merge feature.
compress_algorithm=%s	 Control compress algorithm, currently f2fs supports "lzo",
			 "lz4", "zstd" and "lzo-rle" algorithm.
compress_algorithm=%s:%d Control compress algorithm and its compress level, now, only
			 "lz4" and "zstd" support compress level config.

			 =========      ===========
			 algorithm      level range
			 =========      ===========
			 lz4            3 - 16
			 zstd           1 - 22
			 =========      ===========
compress_log_size=%u	 Support configuring compress cluster size. The size will
			 be 4KB * (1 << %u). The default and minimum sizes are 16KB.
compress_extension=%s	 Support adding specified extension, so that f2fs can enable
			 compression on those corresponding files, e.g. if all files
			 with '.ext' has high compression rate, we can set the '.ext'
			 on compression extension list and enable compression on
			 these file by default rather than to enable it via ioctl.
			 For other files, we can still enable compression via ioctl.
			 Note that, there is one reserved special extension '*', it
			 can be set to enable compression for all files.
nocompress_extension=%s	 Support adding specified extension, so that f2fs can disable
			 compression on those corresponding files, just contrary to compression extension.
			 If you know exactly which files cannot be compressed, you can use this.
			 The same extension name can't appear in both compress and nocompress
			 extension at the same time.
			 If the compress extension specifies all files, the types specified by the
			 nocompress extension will be treated as special cases and will not be compressed.
			 Don't allow use '*' to specifie all file in nocompress extension.
			 After add nocompress_extension, the priority should be:
			 dir_flag < comp_extention,nocompress_extension < comp_file_flag,no_comp_file_flag.
			 See more in compression sections.

compress_chksum		 Support verifying chksum of raw data in compressed cluster.
compress_mode=%s	 Control file compression mode. This supports "fs" and "user"
			 modes. In "fs" mode (default), f2fs does automatic compression
			 on the compression enabled files. In "user" mode, f2fs disables
			 the automaic compression and gives the user discretion of
			 choosing the target file and the timing. The user can do manual
			 compression/decompression on the compression enabled files using
			 ioctls.
compress_cache		 Support to use address space of a filesystem managed inode to
			 cache compressed block, in order to improve cache hit ratio of
			 random read.
inlinecrypt		 When possible, encrypt/decrypt the contents of encrypted
			 files using the blk-crypto framework rather than
			 filesystem-layer encryption. This allows the use of
			 inline encryption hardware. The on-disk format is
			 unaffected. For more details, see
			 Documentation/block/inline-encryption.rst.
atgc			 Enable age-threshold garbage collection, it provides high
			 effectiveness and efficiency on background GC.
discard_unit=%s		 Control discard unit, the argument can be "block", "segment"
			 and "section", issued discard command's offset/size will be
			 aligned to the unit, by default, "discard_unit=block" is set,
			 so that small discard functionality is enabled.
			 For blkzoned device, "discard_unit=section" will be set by
			 default, it is helpful for large sized SMR or ZNS devices to
			 reduce memory cost by getting rid of fs metadata supports small
			 discard.
memory=%s		 Control memory mode. This supports "normal" and "low" modes.
			 "low" mode is introduced to support low memory devices.
			 Because of the nature of low memory devices, in this mode, f2fs
			 will try to save memory sometimes by sacrificing performance.
			 "normal" mode is the default mode and same as before.
age_extent_cache	 Enable an age extent cache based on rb-tree. It records
			 data block update frequency of the extent per inode, in
			 order to provide better temperature hints for data block
			 allocation.
errors=%s		 Specify f2fs behavior on critical errors. This supports modes:
			 "panic", "continue" and "remount-ro", respectively, trigger
			 panic immediately, continue without doing anything, and remount
			 the partition in read-only mode. By default it uses "continue"
			 mode.

			 ====================== =============== =============== ========
			 mode                   continue        remount-ro      panic
			 ====================== =============== =============== ========
			 access ops             normal          normal          N/A
			 syscall errors         -EIO            -EROFS          N/A
			 mount option           rw              ro              N/A
			 pending dir write      keep            keep            N/A
			 pending non-dir write  drop            keep            N/A
			 pending node write     drop            keep            N/A
			 pending meta write     keep            keep            N/A
			 ====================== =============== =============== ========
nat_bits		 Enable nat_bits feature to enhance full/empty nat blocks access,
			 by default it's disabled.
lookup_mode=%s		 Control the directory lookup behavior for casefolded
			 directories. This option has no effect on directories
			 that do not have the casefold feature enabled.

			 ================== ========================================
			 Value              Description
			 ================== ========================================
			 perf               (Default) Enforces a hash-only lookup.
					    The linear search fallback is always
					    disabled, ignoring the on-disk flag.
			 compat             Enables the linear search fallback for
					    compatibility with directory entries
					    created by older kernel that used a
					    different case-folding algorithm.
					    This mode ignores the on-disk flag.
			 auto               F2FS determines the mode based on the
					    on-disk `SB_ENC_NO_COMPAT_FALLBACK_FL`
					    flag.
			 ================== ========================================
======================== ============================================================
