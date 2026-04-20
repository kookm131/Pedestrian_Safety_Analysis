import sys
from unittest.mock import MagicMock

# Mock out heavy or missing dependencies
sys.modules["database"] = MagicMock()
sys.modules["ultralytics"] = MagicMock()
sys.modules["cv2"] = MagicMock()

import json
from backend.main import app

def export_openapi():
    # FastAPI computes the schema when app.openapi() is called
    schema = app.openapi()
    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    print("Successfully exported openapi.json")

if __name__ == "__main__":
    export_openapi()
