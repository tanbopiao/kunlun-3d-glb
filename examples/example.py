"""示例：现场封一匣、验一匣、开一匣——拿到手即可跑通。"""

import json
import tempfile
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kunlun_glb import KunlunGlb  # noqa: E402

# 1) 封匣：神识（结构）＋ 肉身（顶点数据）装进一匣
gltf = {
    "asset": {"version": "2.0"},
    "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}],
    "accessors": [{
        "bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3",
        "min": [0.0, 0.0, 0.0], "max": [1.0, 1.0, 1.0],
    }],
    "bufferViews": [{"buffer": 0, "byteLength": 36}],
    "buffers": [{"byteLength": 36}],
}
vertices = struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 1, 0)
raw = KunlunGlb.build(gltf, vertices)

# 2) 验匣与造册：不合制的匣进不来，合制的匣有清册
box = KunlunGlb.from_bytes(raw)
print("造册：", json.dumps(box.stats(), ensure_ascii=False))
print("摘要：", box.digest())

# 3) 开匣：神识与肉身分卷落盘
with tempfile.TemporaryDirectory() as td:
    json_path = os.path.join(td, "scene.gltf")
    bin_path = os.path.join(td, "scene.bin")
    box.extract(json_path, bin_path)
    print("神识卷：", json_path)
    print("肉身卷：", bin_path, f"（{os.path.getsize(bin_path)} 字节）")
