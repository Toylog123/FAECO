"""ISCAS89 扩面 9 例前处理（WSL 内运行版本）。

只把 `module dff ... endmodule` 替换为行为级写法，其余字节保留。
与 Windows 版脚本逻辑等价；本版用 POSIX 路径，供 WSL python3 执行。
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
SRC = ROOT / "data/raw/benchmarks/raw/iscas89"
# 输出目录可由第一个参数指定（缺省沿用 20261029_iscas89_full17）
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    ROOT / "experiments/20261029_iscas89_full17/_preprocessed"
CIRCUITS = ["s298", "s344", "s349", "s386", "s400", "s444", "s510", "s526", "s838"]

BEHAVIORAL = """module dff (CK,Q,D);
input CK,D;
output Q;
reg Q;
always @ (posedge CK)
  Q <= D;
endmodule
"""


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


OUT.mkdir(parents=True, exist_ok=True)
report = []
for c in CIRCUITS:
    p = SRC / f"{c}.v"
    raw = p.read_bytes()
    text = raw.decode("utf-8", errors="strict")
    m = re.search(r"module\s+dff\s*\([^;]*;.*?\nendmodule", text, re.S)
    assert m, f"{c}: 找不到 module dff"
    assert len(re.findall(r"module\s+dff\s*\(", text)) == 1, f"{c}: dff 模块不唯一"
    new = text[: m.start()] + BEHAVIORAL.rstrip("\n") + text[m.end():]
    dst = OUT / f"{c}.gate.v"
    dst.write_bytes(new.encode("utf-8"))
    assert "trireg" not in new and " nmos " not in new, f"{c}: 仍有晶体管原语"
    report.append({
        "circuit": c,
        "raw_bytes": len(raw),
        "raw_sha256": sha(raw),
        "gate_bytes": len(new.encode()),
        "gate_sha256": sha(new.encode()),
        "transformation": "module dff (transistor-level, trireg/nmos) -> behavioral always @(posedge CK)",
    })
    print(f"{c}: {len(raw)} -> {len(new.encode())} B  {sha(raw)[:12]} -> {sha(new.encode())[:12]}")

(OUT / "PREPROCESS_NOTICE.txt").write_text(
    "ISCAS89 扩面 9 例的前处理说明\n"
    "==============================\n\n"
    "原归档 data/raw/benchmarks/raw/iscas89/ 下 17 个电路中，8 个（论文已用）的 dff 是行为级\n"
    "（reg Q; always @(posedge CK) Q <= D;），另 9 个是晶体管级（trireg + nmos + not）。\n"
    "两种方言无法用同一 yosys 流程映射：晶体管级写法在 read_verilog 阶段即报语法错误\n"
    "（trireg 不被 Verilog-2005 前端接受）。\n\n"
    "本目录的 <c>.gate.v 只做了**一处**替换：把 module dff 的整体实现换成与其余 8 例\n"
    "完全相同的行为级写法，文件其余内容逐字节保留。这是 ISCAS89 的常规解释（DFF 语义不变），\n"
    "但属于可追溯的前处理，故保留原文件、记录前后 sha。\n\n"
    "生成与映射均在 WSL 内完成（scripts/wsl_phys17.sh），Windows 侧不参与。\n"
    "映射工具：Yosys 0.67+146（oss-cad-suite nightly 20260804，Linux x64）—— 与主实验\n"
    "experiments/20260826_iscas89_main 同一构建谱系；该版本重映射 s641 可逐字节复现主实验\n"
    "mapped.v（sha 3665ba30...），已在守门步骤校验。\n",
    encoding="utf-8",
)
(OUT / "preprocess_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print("\n->", OUT)
