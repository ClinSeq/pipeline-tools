#!/usr/bin/env python

"""bed_to_regions.py
Convert a BED file to chr:start-stop format. Does not alter coordinates.
"""

import sys

for line in sys.stdin:
    line = line.strip()
    items = line.split("\t")
    # if we're not reading the header
    if not line.startswith("@") and not line.startswith("#") and len(items) > 2:
        sys.stdout.write(
            str(items[0]) +
            ":" +
            str(items[1]) +
            "-" +
            str(items[2]) + 
            "\n"
        )

