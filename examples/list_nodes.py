"""Print the node names in the bundled FModel example."""
import json
from pathlib import Path

example = Path(__file__).with_name("ABP_Ch002_demo.json")
for export in json.loads(example.read_text(encoding="utf-8")):
    for name in export.get("Properties", {}):
        if name.startswith("AnimGraphNode_"):
            print(name)

