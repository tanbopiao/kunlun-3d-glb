"""昆仑三维法相匣 —— 纯标准库 GLB 容器内核（kunlun-3d-glb）

道统出处：昆仑为藏珍之山，洞天藏三维法相；GLB 者，法相之匣——
JSON 神识（结构）与 BIN 肉身（几何数据）共居一匣。
工程映射：纯标准库的 GLB 容器解析与重封装内核——
验匣（魔数/总长/对齐）、造册（结构统计与包围盒）、封匣（重封装补齐对齐）、
摘要（SHA-256，篡改现形）。

# 生长记录 2026-11-28：内核 v0.1 落地，五域回归全绿
"""

import hashlib
import json
import struct

GLB_MAGIC = 0x46546C67      # "glTF"
JSON_CHUNK_TYPE = 0x4E4F534A  # "JSON"
BIN_CHUNK_TYPE = 0x004E4942   # "BIN\0"

_HEADER_SIZE = 12
_CHUNK_HEADER_SIZE = 8
_ALIGNMENT = 4


class GlbFormatError(ValueError):
    """匣不合制：魔数、总长、分块对齐或结构次序违背 GLB 容器规范。"""


def _pad(data, pad_byte):
    """补齐至 4 字节对齐：JSON 块补空格（0x20），BIN 块补零（0x00）。"""
    remainder = len(data) % _ALIGNMENT
    if remainder:
        data += bytes([pad_byte]) * (_ALIGNMENT - remainder)
    return data


class KunlunGlb:
    """法相之匣：解析、验匣、造册、封匣、摘要。"""

    def __init__(self, raw, version, gltf, bin_chunk, unknown_chunks):
        self._raw = raw
        self.version = version
        self.gltf = gltf
        self.bin = bin_chunk
        self.unknown_chunks = unknown_chunks  # 跳过的未知块类型（按规范跳过不报错）

    # ---- 验匣域 ----
    @classmethod
    def from_bytes(cls, raw):
        """解析 GLB 容器：魔数、总长、分块对齐与次序逐项验匣，不合制即拒。"""
        if len(raw) < _HEADER_SIZE:
            raise GlbFormatError(f"匣身过短：{len(raw)} 字节，不足 12 字节头")
        magic, version, total_length = struct.unpack_from("<III", raw, 0)
        if magic != GLB_MAGIC:
            raise GlbFormatError(f"魔数不合：0x{magic:08X}，应为 0x{GLB_MAGIC:08X}（glTF）")
        if total_length != len(raw):
            raise GlbFormatError(f"总长不符：头声明 {total_length} 字节，实得 {len(raw)} 字节")

        json_chunk = None
        bin_chunk = None
        unknown_chunks = []
        offset = _HEADER_SIZE
        while offset < len(raw):
            if offset + _CHUNK_HEADER_SIZE > len(raw):
                raise GlbFormatError("分块头残缺：块头越出匣尾")
            chunk_length, chunk_type = struct.unpack_from("<II", raw, offset)
            offset += _CHUNK_HEADER_SIZE
            if chunk_length % _ALIGNMENT != 0:
                raise GlbFormatError(f"分块不对齐：块长 {chunk_length} 非 4 的倍数")
            if offset + chunk_length > len(raw):
                raise GlbFormatError(f"分块越界：块长 {chunk_length} 越出匣尾")
            data = raw[offset:offset + chunk_length]
            offset += chunk_length
            if chunk_type == JSON_CHUNK_TYPE:
                if json_chunk is not None:
                    raise GlbFormatError("神识重复：JSON 块至多一块")
                json_chunk = data
            elif chunk_type == BIN_CHUNK_TYPE:
                if bin_chunk is not None:
                    raise GlbFormatError("肉身重复：BIN 块至多一块")
                bin_chunk = data
            else:
                unknown_chunks.append(chunk_type)  # 规范允许：未知块跳过并留痕
        if json_chunk is None:
            raise GlbFormatError("神识缺失：未找到 JSON 块")
        try:
            gltf = json.loads(json_chunk.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GlbFormatError(f"神识不可读：JSON 解析失败（{exc}）") from exc
        return cls(raw, version, gltf, bin_chunk, unknown_chunks)

    @classmethod
    def from_file(cls, path):
        with open(path, "rb") as fh:
            return cls.from_bytes(fh.read())

    # ---- 造册域 ----
    def stats(self):
        """造册：结构清点与位置包围盒，外人不用问人即可知匣中所藏。"""
        gltf = self.gltf
        counts = {
            key: len(gltf.get(key) or [])
            for key in ("scenes", "nodes", "meshes", "accessors", "bufferViews",
                        "buffers", "materials", "textures", "images")
        }
        counts["unknown_chunks"] = len(self.unknown_chunks)
        counts["has_bin"] = self.bin is not None
        bounds = self.position_bounds()
        if bounds is not None:
            lo, hi = bounds
            counts["position_min"] = [round(v, 6) for v in lo]
            counts["position_max"] = [round(v, 6) for v in hi]
        return counts

    def position_bounds(self):
        """位置包围盒：遍历网格 POSITION 访问器的 min/max；无则 None。"""
        lo = hi = None
        for mesh in self.gltf.get("meshes") or []:
            for prim in mesh.get("primitives") or []:
                acc_index = (prim.get("attributes") or {}).get("POSITION")
                if acc_index is None:
                    continue
                acc = (self.gltf.get("accessors") or [])[acc_index]
                acc_min, acc_max = acc.get("min"), acc.get("max")
                if acc_min is None or acc_max is None:
                    continue
                lo = acc_min if lo is None else [min(a, b) for a, b in zip(lo, acc_min)]
                hi = acc_max if hi is None else [max(a, b) for a, b in zip(hi, acc_max)]
        return (lo, hi) if lo is not None else None

    # ---- 摘要域 ----
    def digest(self):
        """摘要：SHA-256(原字节)。同匣同摘，一字之改必现形。"""
        return hashlib.sha256(self._raw).hexdigest()

    # ---- 提取域 ----
    def extract(self, json_path, bin_path=None):
        """开匣：神识与肉身分写两卷；肉身缺位时跳过。"""
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(self.gltf, fh, ensure_ascii=False, indent=2)
        if bin_path is not None and self.bin is not None:
            with open(bin_path, "wb") as fh:
                fh.write(self.bin)

    # ---- 封匣域 ----
    @classmethod
    def build(cls, gltf, bin_data=b""):
        """封匣：神识补空格、肉身补零，4 字节对齐，重装一匣。"""
        if not isinstance(gltf, dict):
            raise GlbFormatError("神识须为 JSON 对象（dict）")
        json_data = json.dumps(gltf, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        json_data = _pad(json_data, 0x20)
        bin_data = bytes(bin_data)
        bin_padded = _pad(bin_data, 0x00)

        chunks = [(JSON_CHUNK_TYPE, json_data)]
        if bin_data:
            chunks.append((BIN_CHUNK_TYPE, bin_padded))
        total = _HEADER_SIZE + sum(_CHUNK_HEADER_SIZE + len(d) for _, d in chunks)
        out = struct.pack("<III", GLB_MAGIC, 2, total)
        for chunk_type, data in chunks:
            out += struct.pack("<II", len(data), chunk_type) + data
        return out

    def save(self, path):
        with open(path, "wb") as fh:
            fh.write(self._raw)

    def describe(self):
        return {
            "name": "kunlun-3d-glb",
            "role": "三维法相匣 · GLB 容器内核",
            "version": self.version,
            "unknown_chunks": len(self.unknown_chunks),
            "has_bin": self.bin is not None,
        }
