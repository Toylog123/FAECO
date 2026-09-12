# Scripts

本目录保存可重复执行的命令行脚本。

## 现有脚本

| 脚本 | 用途 | 用法 |
|---|---|---|
| `check_toolchain.ps1` | 检测 Python、Yosys、ABC、OpenSTA、Z3 和 NetworkX，并输出 JSON | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_toolchain.ps1 -OutputPath experiments/environment/toolchain_<date>.json` |
| `run_minimal_combinational_demo.py` | 跑通单 case 或配置驱动 batch combinational demo，并写入独立实验目录 | `python scripts/run_minimal_combinational_demo.py` 或 `python scripts/run_minimal_combinational_demo.py --config experiments/configs/minimal_combinational.json --output-dir experiments/20260718_minimal_combinational_batch_demo` |
| `make_minimal_case_variant.py` | 从已有 case 派生另一个 target-output case | `python scripts/make_minimal_case_variant.py --source-case-dir ... --output-case-dir ... --target-output ... --force` |
| `make_minimal_case_from_raw.py` | 从本地 raw Verilog 生成最小 ECO case | `python scripts/make_minimal_case_from_raw.py --raw-verilog benchmarks/raw/iscas85/c432.v --output-case-dir data/cases/minimal/iscas85_c432_case01 --case-id iscas85_c432_case01 --suite ISCAS85 --circuit c432 --target-output N432 --force` |
| `make_minimal_case_from_bench.py` | 从本地 ISCAS-style `.bench` 文件生成最小 ECO case | `python scripts/make_minimal_case_from_bench.py --bench benchmarks/raw/iscas85/<name>.bench --output-case-dir data/cases/minimal/<case_id> --case-id <case_id> --suite ISCAS85 --circuit <name> --target-output <output>` |

## 当前注意事项

- batch runner 重跑时会清理输出目录中的旧 `raw_results/` 和 `tables/`，避免 stale run 影响实验追溯。
- raw/BENCH 导入脚本当前只复制同一 netlist 到 `original/` 和 `resynthesized/`，用于原型闭环；真实 resynthesis 仍待接入。
- 真实 benchmark 新语法必须先补测试再扩展 parser/importer。
