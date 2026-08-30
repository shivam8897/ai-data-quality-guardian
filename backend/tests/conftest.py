import os
import sys

# Allow `from profiler...` / `from anomaly...` imports the same way main.py does,
# since these packages use bare (non-package-relative) sibling imports.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
