#!/usr/bin/env python3
"""Make native preview extract and compile the exact German Pip-Boy date formatter."""
from pathlib import Path
import sys

preview = Path(sys.argv[1]) / "audit/device-ui-preview.py"
source = preview.read_text(encoding="utf-8")
needle = "names = '''trimTrailingZeros"
if needle not in source:
    raise SystemExit("Native preview function list changed; refusing to patch blindly")
source = source.replace(needle, "names = '''formatPipboyGermanDate trimTrailingZeros", 1)
lines = source.splitlines()
matches = [i for i, line in enumerate(lines) if line.startswith("code = '#include")]
if len(matches) != 1:
    raise SystemExit("Native preview C++ preamble changed; refusing to patch blindly")
lines[matches[0]] = """code = '#include "device-ui-fixture.h"\\n#include <ctime>\\n' + palette"""
preview.write_text("\\n".join(lines) + "\\n", encoding="utf-8")
print("Native preview extracts the actual German date formatter from display.cpp")
