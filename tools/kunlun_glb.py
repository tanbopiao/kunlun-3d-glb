#!/usr/bin/env python3
"""昆仑三维法相匣 · 命令行工具

用法：
  python tools/kunlun_glb.py inspect  <file.glb>          造册：结构清点与包围盒
  python tools/kunlun_glb.py digest   <file.glb>          摘要：SHA-256
  python tools/kunlun_glb.py extract  <file.glb> <outdir> 开匣：神识与肉身分卷
  python tools/kunlun_glb.py build    <in.gltf> <out.glb> [in.bin]  封匣：重装一匣
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kunlun_glb import KunlunGlb  # noqa: E402


def cmd_inspect(args):
    box = KunlunGlb.from_file(args.file)
    print(json.dumps(box.stats(), ensure_ascii=False, indent=2))


def cmd_digest(args):
    box = KunlunGlb.from_file(args.file)
    print(box.digest())


def cmd_extract(args):
    box = KunlunGlb.from_file(args.file)
    os.makedirs(args.outdir, exist_ok=True)
    json_path = os.path.join(args.outdir, "scene.gltf")
    bin_path = os.path.join(args.outdir, "scene.bin")
    box.extract(json_path, bin_path)
    print(f"神识 → {json_path}")
    if os.path.exists(bin_path):
        print(f"肉身 → {bin_path}")


def cmd_build(args):
    with open(args.gltf, encoding="utf-8") as fh:
        gltf = json.load(fh)
    bin_data = b""
    if args.bin:
        with open(args.bin, "rb") as fh:
            bin_data = fh.read()
    raw = KunlunGlb.build(gltf, bin_data)
    with open(args.out, "wb") as fh:
        fh.write(raw)
    print(f"封匣完成 → {args.out}（{len(raw)} 字节）")


def main():
    parser = argparse.ArgumentParser(description="昆仑三维法相匣 · GLB 容器内核")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("inspect", help="造册：结构清点与包围盒")
    p.add_argument("file")
    p.set_defaults(func=cmd_inspect)

    p = sub.add_parser("digest", help="摘要：SHA-256")
    p.add_argument("file")
    p.set_defaults(func=cmd_digest)

    p = sub.add_parser("extract", help="开匣：神识与肉身分卷")
    p.add_argument("file")
    p.add_argument("outdir")
    p.set_defaults(func=cmd_extract)

    p = sub.add_parser("build", help="封匣：重装一匣")
    p.add_argument("gltf")
    p.add_argument("out")
    p.add_argument("bin", nargs="?")
    p.set_defaults(func=cmd_build)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
