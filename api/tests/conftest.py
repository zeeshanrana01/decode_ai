import sys
from pathlib import Path

# Add api directory to sys.path so 'app' is discoverable
API_ROOT = Path(__file__).resolve().parent.parent
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))
