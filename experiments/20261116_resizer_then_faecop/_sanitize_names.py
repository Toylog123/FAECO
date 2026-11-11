import re, pathlib, sys

circuits = sys.argv[1:] or ["s382"]
pat = re.compile(r"\\([A-Za-z0-9_]+)/_0_")          # \DFF_14/_0_
esc = re.compile(r"\\[A-Za-z0-9_]+/[A-Za-z0-9_]+")   # any remaining \X/Y

for c in circuits:
    src = pathlib.Path(f"experiments/20261116_resizer_then_faecop/exports/{c}/resized_gate.v")
    dst = pathlib.Path(f"experiments/20261116_resizer_then_faecop/exports/{c}/resized_gate_flat.v")
    text = src.read_text(encoding="utf-8")
    # \DFF_14/_0_  ->  DFF_14   (make the flattened FF instance look like the
    # hierarchical W1 instance name so the mechanism's FF model applies)
    new = pat.sub(r"\1", text)
    dst.write_text(new, encoding="utf-8")
    left = esc.findall(new)
    print(f"[{c}] wrote {dst} chars={len(new)} rewrites={len(pat.findall(text))} leftover={len(left)}")