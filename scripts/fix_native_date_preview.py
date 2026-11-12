#!/usr/bin/env python3
"""Make native preview extraction include the actual German Pip-Boy date formatter."""
from pathlib import Path
import sys

preview = Path(sys.argv[1]) / "audit/device-ui-preview.py"
source = preview.read_text(encoding="utf-8")
needle = "trimTrailingZeros groupThousands"
if needle not in source:
    raise SystemExit("Native preview function list changed; refusing to patch blindly")
if "formatPipboyGermanDate" not in source:
    source = source.replace(needle, "formatPipboyGermanDate " + needle, 1)
needle = "code = '#include \"device-ui-fixture.h\"\\n' + palette"
replacement = "code = '#include \"device-ui-fixture.h\"\\n#include <ctime>\\n' + palette"
if needle not in source:
    raise SystemExit("Native preview C++ preamble changed; refusing to patch blindly")
source = source.replace(needle, replacement, 1)
preview.write_text(source, encoding="utf-8")
print("Native preview now compiles and renders the real German date formatter")
