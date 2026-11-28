# kunlun-3d-glb 昆仑三维法相匣

法相之匣的容器内核：验匣、造册、开匣、封匣、摘要，纯标准库。

｜元枢体系 YUANSHU

## 定名语义

- 道统出处：昆仑为藏珍之山，洞天藏三维法相；GLB 者，法相之匣——JSON 神识与 BIN 肉身共居一匣
- 工程映射：纯标准库的 GLB 容器解析与重封装内核——不合制的匣进不来，合制的匣有清册，一字之改必现形

## 这是什么

一个纯标准库的 GLB（glTF 二进制）容器内核：解析 12 字节头与分块结构，逐项验匣（魔数、总长、4 字节对齐、块次序），不合制即拒；合制的匣可清点结构（网格、访问器、缓冲视图书册）并读出位置包围盒；神识（JSON 块）与肉身（BIN 块）可分卷提取，也可从结构加数据重装一匣（自动补齐对齐）；任意一匣都有 SHA-256 摘要，一字之改必现形。

## 道统映射

| 道统名 | 内核对象 | 职责 |
|--------|----------|------|
| 验匣 | `KunlunGlb.from_bytes` | 魔数、总长、对齐、次序逐项核验，违者 `GlbFormatError` |
| 神识 | `.gltf` | JSON 结构块：场景、节点、网格、访问器 |
| 肉身 | `.bin` | BIN 数据块：几何缓冲原样可取 |
| 造册 | `stats` | 结构清点＋位置包围盒，无则不造数 |
| 封匣 | `build` | 重装一匣：神识补空格、肉身补零，4 字节对齐 |
| 摘要 | `digest` | SHA-256(原字节)，同匣同摘，篡改现形 |

## 快速开始

```python
from kunlun_glb import KunlunGlb

raw = KunlunGlb.build(gltf_dict, bin_bytes)   # 封匣：自动补齐对齐
box = KunlunGlb.from_bytes(raw)               # 验匣：不合制即拒
print(box.stats())                            # 造册：结构清点＋包围盒
print(box.digest())                           # 摘要：SHA-256
box.extract("scene.gltf", "scene.bin")        # 开匣：神识与肉身分卷
```

命令行：

```bash
python tools/kunlun_glb.py inspect  model.glb
python tools/kunlun_glb.py digest   model.glb
python tools/kunlun_glb.py extract  model.glb outdir/
python tools/kunlun_glb.py build    scene.gltf out.glb scene.bin
```

## 设计约定

- 纯标准库（`struct`/`json`/`hashlib`），无第三方依赖。
- 验匣从严：魔数、总长、块对齐、重复块、缺失神识一律 `GlbFormatError`，不静默放行。
- 未知块类型按规范跳过，但留痕于 `unknown_chunks`，不丢失信息。
- 摘要基于原始字节：任何一字被改，摘要必不一致——「篡改现形」是本内核的第一契约。

## 回归

`regression.md` 登记回归铁律（容器、神识、肉身、封匣、摘要五域契约）。运行：

```bash
python3 -m unittest discover -s . -p "test_*.py"
```

## 许可证

MIT。仓库：<https://github.com/tanbopiao/kunlun-3d-glb>
