import sys
sys.path.insert(0, r"D:/BaiduSyncdisk/03_FAECO/src")
from pathlib import Path
from rseco.netlist import apply_sizing
ROOT = Path(r"D:/BaiduSyncdisk/03_FAECO")
mapped = ROOT / "experiments/20260806_b19_067_repair/b19/mapped.v"
text = mapped.read_text(encoding="utf-8", errors="replace")
new_text = apply_sizing(text, {"_1254713_": "sky130_fd_sc_hd__a211oi_4"})
rep = ROOT / "experiments/20260806_b19_067_repair/b19/repaired.v"
rep.write_text(new_text, encoding="utf-8")
# verify the replacement happened
print("a211oi_4 count:", new_text.count("sky130_fd_sc_hd__a211oi_4"))
print("a211oi_1 count:", new_text.count("sky130_fd_sc_hd__a211oi_1"))
print("repaired written:", rep)