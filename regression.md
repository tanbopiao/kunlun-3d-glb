# 回归铁律 · kunlun-3d-glb

五域契约，任何改动不得破例：

| 域 | 铁律 | 用例 |
|----|------|------|
| 容器域 | 魔数、总长、块对齐、块次序逐项验匣；违者 GlbFormatError，不静默 | test_bad_magic / test_total_length_mismatch / test_unaligned_chunk_length / test_duplicate_json_chunk |
| 神识域 | JSON 结构清点如实；POSITION 包围盒取自访问器 min/max，无则不造数 | test_stats_counts / test_position_bounds_from_accessor |
| 肉身域 | BIN 数据原样可取；开匣分卷不损一字 | test_bin_chunk_accessible / test_extract_writes_files |
| 封匣域 | 重封装补齐 4 字节对齐（神识补空格、肉身补零），往返一致 | test_build_roundtrip / test_build_padding_aligned |
| 摘要域 | 同匣同摘；一字之改必现形（篡改现形铁律） | test_digest_stable / test_tampered_byte_manifests_in_digest |

运行：

```bash
python3 -m unittest discover -s . -p "test_*.py"
```
