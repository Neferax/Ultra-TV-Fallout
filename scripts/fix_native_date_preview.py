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
needle = "code = '#include \\"device-ui-fixture.h\\"\\n' + palette"
if needle not in source:
    raise SystemExit("Native preview C++ preamble changed; refusing to patch blindly")
source = source.replace(needle, "code = '#include \\"device-ui-fixture.h\\"\\n#include <ctime>\\n' + palette", 1)
preview.write_text(source, encoding="utf-8")
print("Native preview extracts the actual German date formatter from display.cpp")
