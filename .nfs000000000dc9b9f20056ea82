"""昆仑三维法相匣 · 五域回归（容器/神识/肉身/封匣/摘要）

回归铁律见 regression.md。全部夹具由 struct 现场构筑，不依赖外部资产文件。
"""

import hashlib
import json
import os
import struct
import tempfile
import unittest

from kunlun_glb import (
    BIN_CHUNK_TYPE,
    GLB_MAGIC,
    JSON_CHUNK_TYPE,
    GlbFormatError,
    KunlunGlb,
)

MIN_GLTF = {"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": []}]}


def make_glb(gltf=None, bin_data=b"", extra_chunk=None, total_length=None,
             magic=GLB_MAGIC, version=2):
    """现场构筑 GLB 夹具：默认合法，逐参数注入破绽。"""
    gltf = MIN_GLTF if gltf is None else gltf
    json_data = json.dumps(gltf, ensure_ascii=False).encode("utf-8")
    json_data += b" " * (-len(json_data) % 4)
    chunks = [(JSON_CHUNK_TYPE, json_data)]
    if bin_data:
        bin_padded = bin_data + b"\x00" * (-len(bin_data) % 4)
        chunks.append((BIN_CHUNK_TYPE, bin_padded))
    if extra_chunk is not None:
        chunks.append(extra_chunk)
    total = 12 + sum(8 + len(d) for _, d in chunks)
    if total_length is not None:
        total = total_length
    out = struct.pack("<III", magic, version, total)
    for ctype, data in chunks:
        out += struct.pack("<II", len(data), ctype) + data
    return out


GLTF_WITH_MESH = {
    "asset": {"version": "2.0"},
    "meshes": [{
        "primitives": [{
            "attributes": {"POSITION": 0},
        }],
    }],
    "accessors": [{
        "bufferView": 0,
        "componentType": 5126,
        "count": 3,
        "type": "VEC3",
        "min": [-1.0, -2.0, -3.0],
        "max": [1.0, 2.0, 3.0],
    }],
    "bufferViews": [{"buffer": 0, "byteLength": 36}],
    "buffers": [{"byteLength": 36}],
}


class ContainerDomain(unittest.TestCase):
    """容器域：验匣铁律——魔数、总长、对齐、次序，违者即拒。"""

    def test_valid_minimal_parses(self):
        box = KunlunGlb.from_bytes(make_glb())
        self.assertEqual(box.version, 2)
        self.assertEqual(box.gltf["asset"]["version"], "2.0")

    def test_bad_magic_rejected(self):
        with self.assertRaises(GlbFormatError):
            KunlunGlb.from_bytes(make_glb(magic=0x12345678))

    def test_truncated_header_rejected(self):
        with self.assertRaises(GlbFormatError):
            KunlunGlb.from_bytes(b"\x00" * 8)

    def test_total_length_mismatch_rejected(self):
        with self.assertRaises(GlbFormatError):
            KunlunGlb.from_bytes(make_glb(total_length=99999))

    def test_unaligned_chunk_length_rejected(self):
        raw = make_glb()
        # 把 JSON 块长改成非 4 倍数：篡改一字，验匣必现形
        patched = bytearray(raw)
        struct.pack_into("<I", patched, 12, struct.unpack_from("<I", raw, 12)[0] + 1)
        with self.assertRaises(GlbFormatError):
            KunlunGlb.from_bytes(bytes(patched))

    def test_missing_json_chunk_rejected(self):
        raw = make_glb()
        body = raw[12:]
        bin_only = struct.pack("<III", GLB_MAGIC, 2, 12 + len(body)) + \
            struct.pack("<II", len(body), BIN_CHUNK_TYPE) + body
        with self.assertRaises(GlbFormatError):
            KunlunGlb.from_bytes(bin_only)

    def test_duplicate_json_chunk_rejected(self):
        raw = make_glb()
        json_body = raw[20:20 + struct.unpack_from("<I", raw, 12)[0]]
        dup = raw + struct.pack("<II", len(json_body), JSON_CHUNK_TYPE) + json_body
        dup = dup[:8] + struct.pack("<I", len(dup), ) + dup[12:]
        with self.assertRaises(GlbFormatError):
            KunlunGlb.from_bytes(dup)

    def test_json_decode_error_rejected(self):
        broken = make_glb(gltf=None)  # 占位，下面手工造坏 JSON
        json_body = b'{"asset": broken'
        json_body += b" " * (-len(json_body) % 4)
        total = 12 + 8 + len(json_body)
        raw = struct.pack("<III", GLB_MAGIC, 2, total) + \
            struct.pack("<II", len(json_body), JSON_CHUNK_TYPE) + json_body
        with self.assertRaises(GlbFormatError):
            KunlunGlb.from_bytes(raw)
        del broken

    def test_unknown_chunk_skipped_and_recorded(self):
        raw = make_glb(extra_chunk=(0xDEADBEEF, b"\x00" * 4))
        box = KunlunGlb.from_bytes(raw)
        self.assertEqual(box.unknown_chunks, [0xDEADBEEF])
        self.assertEqual(box.gltf["asset"]["version"], "2.0")

    def test_no_bin_chunk_ok(self):
        box = KunlunGlb.from_bytes(make_glb())
        self.assertIsNone(box.bin)


class ShenshiDomain(unittest.TestCase):
    """神识域：JSON 结构清点与位置包围盒。"""

    def test_stats_counts(self):
        box = KunlunGlb.from_bytes(make_glb(GLTF_WITH_MESH, bin_data=b"\x00" * 36))
        stats = box.stats()
        self.assertEqual(stats["meshes"], 1)
        self.assertEqual(stats["accessors"], 1)
        self.assertEqual(stats["bufferViews"], 1)
        self.assertTrue(stats["has_bin"])

    def test_position_bounds_from_accessor(self):
        box = KunlunGlb.from_bytes(make_glb(GLTF_WITH_MESH))
        lo, hi = box.position_bounds()
        self.assertEqual(lo, [-1.0, -2.0, -3.0])
        self.assertEqual(hi, [1.0, 2.0, 3.0])

    def test_empty_gltf_stats(self):
        box = KunlunGlb.from_bytes(make_glb())
        stats = box.stats()
        self.assertEqual(stats["meshes"], 0)
        self.assertNotIn("position_min", stats)


class RoushenDomain(unittest.TestCase):
    """肉身域：BIN 数据原样可取，开匣分卷不损一字。"""

    def test_bin_chunk_accessible(self):
        payload = bytes(range(36))
        box = KunlunGlb.from_bytes(make_glb(GLTF_WITH_MESH, bin_data=payload))
        self.assertEqual(box.bin, payload)

    def test_extract_writes_files(self):
        payload = b"\x01\x02\x03\x04"
        box = KunlunGlb.from_bytes(make_glb(GLTF_WITH_MESH, bin_data=payload))
        with tempfile.TemporaryDirectory() as td:
            json_path = os.path.join(td, "scene.gltf")
            bin_path = os.path.join(td, "scene.bin")
            box.extract(json_path, bin_path)
            with open(json_path, encoding="utf-8") as fh:
                self.assertEqual(json.load(fh)["asset"]["version"], "2.0")
            with open(bin_path, "rb") as fh:
                self.assertEqual(fh.read(), payload)


class FengxiaDomain(unittest.TestCase):
    """封匣域：重封装补齐对齐，往返一致。"""

    def test_build_roundtrip(self):
        payload = bytes(range(36))
        raw = KunlunGlb.build(GLTF_WITH_MESH, payload)
        box = KunlunGlb.from_bytes(raw)
        self.assertEqual(box.gltf, GLTF_WITH_MESH)
        self.assertEqual(box.bin, payload)

    def test_build_padding_aligned(self):
        raw = KunlunGlb.build(MIN_GLTF, b"abc")  # 3 字节肉身，须补零对齐
        self.assertEqual(len(raw) % 4, 0)
        magic, version, total = struct.unpack_from("<III", raw, 0)
        self.assertEqual(total, len(raw))
        self.assertEqual(magic, GLB_MAGIC)
        box = KunlunGlb.from_bytes(raw)  # 补齐后仍合制
        self.assertEqual(box.gltf, MIN_GLTF)

    def test_build_rejects_non_dict(self):
        with self.assertRaises(GlbFormatError):
            KunlunGlb.build([1, 2, 3])


class ZhaiyaoDomain(unittest.TestCase):
    """摘要域：同匣同摘，一字之改必现形（篡改现形铁律）。"""

    def test_digest_stable(self):
        raw = make_glb(GLTF_WITH_MESH, bin_data=b"\x00" * 8)
        self.assertEqual(KunlunGlb.from_bytes(raw).digest(),
                         hashlib.sha256(raw).hexdigest())

    def test_tampered_byte_manifests_in_digest(self):
        raw = make_glb(GLTF_WITH_MESH, bin_data=b"\x00" * 8)
        tampered = bytearray(raw)
        tampered[-1] ^= 0xFF  # 肉身末字节翻转
        d1 = KunlunGlb.from_bytes(raw).digest()
        d2 = KunlunGlb.from_bytes(bytes(tampered)).digest()
        self.assertNotEqual(d1, d2)  # 篡改必现形：摘要不一致


if __name__ == "__main__":
    unittest.main()
