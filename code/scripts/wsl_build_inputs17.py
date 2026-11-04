"""为 17 例生成统一输入 `_in/<c>.v`（WSL 内运行）。

规则（同一套，17 例都过）：
- 8 个论文用例：原文照抄；若文件内**未定义** `module dff`（s820/s832/s953 三例如此，
  原文只实例化却未给模型），在文件末尾追加与本项目其余电路相同的行为级 dff 定义。
- 9 个扩面用例：使用 `_preprocessed/<c>.gate.v`（晶体管级 dff 已换成行为级写法，
  见 PREPROCESS_NOTICE.txt）。

目的：让下游 `synth -flatten` 能把触发器展开并真正映射到 sky130 dfxtp，
而不是留成子模块黑盒（主实验族即后者，触发器未进入时序）。
"""
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
SRC = ROOT / "data/raw/benchmarks/raw/iscas89"
OUT = ROOT / "experiments/20261029_iscas17_yosys_latest"
PRE = OUT / "_preprocessed"
IN = OUT / "_in"

BASE8 = ["s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953"]
NEW9 = ["s298", "s344", "s349", "s386", "s400", "s444", "s510", "s526", "s838"]

DFF_MODEL = """
module dff(CK, Q, D);
  input CK, D;
  output Q;
  reg Q;
  always @(posedge CK) Q <= D;
endmodule
"""


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


IN.mkdir(parents=True, exist_ok=True)
report = []
for c in BASE8 + NEW9:
    if c in NEW9:
        src = PRE / f"{c}.gate.v"
        origin = "preprocessed:transistor_dff->behavioral"
    else:
        src = SRC / f"{c}.v"
        origin = "raw"
    raw = src.read_bytes()
    text = raw.decode("utf-8", errors="strict")
    appended = False
    if not re.search(r"module\s+dff\s*\(", text):
        text = text.rstrip("\n") + "\n" + DFF_MODEL
        appended = True
    dst = IN / f"{c}.v"
    dst.write_bytes(text.encode("utf-8"))
    report.append({
        "circuit": c, "origin": origin,
        "dff_model_appended": appended,
        "src_bytes": len(raw), "src_sha256": sha(raw),
        "in_bytes": len(text.encode()), "in_sha256": sha(text.encode()),
    })
    print(f"{c:6s} {origin:38s} dff附加={appended!s:5s} {len(raw):7d} -> {len(text.encode()):7d} B")

(IN / "INPUT_NOTICE.txt").write_text(
    "17 例统一输入说明\n"
    "=================\n\n"
    "1) 8 个论文用例直接取 data/raw/benchmarks/raw/iscas89/<c>.v。其中 s820 / s832 / s953\n"
    "   原文只实例化 `dff` 却**没有给出该模块的定义**（ISCAS89 原始分发里 dff 由外部文件提供）。\n"
    "   为使其可被 flatten，在文件末尾追加与本项目其余电路完全一致的行为级 dff（端口顺序\n"
    "   必须与原分发一致：CK, Q, D —— 原文是位置连接 `dff DFF_0(CK,G38,G90)`，即 Q=G38）：\n"
    "       module dff(CK, Q, D); input CK, D; output Q; reg Q;\n"
    "       always @(posedge CK) Q <= D; endmodule\n"
    "   其余文本逐字节保留。\n\n"
    "2) 9 个扩面用例取 _preprocessed/<c>.gate.v（晶体管级 dff 已换行为级，见该目录说明）。\n\n"
    "3) 映射时使用 `synth -top <c> -flatten`，使 dff 子模块被展开，触发器真正进入\n"
    "   dfflibmap -> sky130_fd_sc_hd__dfxtp_*。\n"
    "   注意：论文主实验的网表**没有** flatten，mapped.v 中 dff 以子模块黑盒残留\n"
    "   （s641 19 个），触发器不参与时序。两族因此在触发器处理上不同，不可直接并列。\n",
    encoding="utf-8",
)
(IN / "inputs_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print("\n->", IN)
