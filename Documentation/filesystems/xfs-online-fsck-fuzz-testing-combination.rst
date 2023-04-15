* For each metadata object existing on the filesystem...

  * For each record inside that metadata object...

    * For each field inside that record...

      * For each conceivable type of transformation that can be applied to a bit field...

        1. Clear all bits
        2. Set all bits
        3. Toggle the most significant bit
        4. Toggle the middle bit
        5. Toggle the least significant bit
        6. Add a small quantity
        7. Subtract a small quantity
        8. Randomize the contents

        * ...test the reactions of:

          1. The kernel verifiers to stop obviously bad metadata
          2. Offline checking (``xfs_repair -n``)
          3. Offline repair (``xfs_repair``)
          4. Online checking (``xfs_scrub -n``)
          5. Online repair (``xfs_scrub``)
          6. Both repair tools (``xfs_scrub`` and then ``xfs_repair`` if
	     online repair doesn't succeed)
