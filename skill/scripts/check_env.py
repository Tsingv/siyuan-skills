from __future__ import annotations

import json

from bootstrap import check_runtime


if __name__ == "__main__":
    print(json.dumps(check_runtime(), ensure_ascii=False, indent=2))
