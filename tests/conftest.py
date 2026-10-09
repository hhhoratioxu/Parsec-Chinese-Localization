import os
# Headless tests exercise widgets; native window integration is checked separately.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
