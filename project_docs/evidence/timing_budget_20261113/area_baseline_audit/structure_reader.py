"""Fail-closed structural comparison of complete flat, named-pin Verilog exports.

This is a narrow gate-netlist reader, not a general Verilog equivalence tool.
It accepts one non-ANSI module, declarations, continuous assignments and
single named-pin instances. Unsupported syntax fails instead of being ignored.
Escaped identifiers are lexed through terminating whitespace; all cells count.
Run from any directory; no EDA tools or third-party packages are required.
"""
import hashlib
import json
from pathlib import Path
import re


TOKEN = re.compile(
    r"(?P<space>\s+)|(?P<line>//[^\n]*)|(?P<block>/\*[\s\S]*?\*/)"
    r"|(?P<escaped>\\[^\s]+)|(?P<id>[A-Za-z_$][A-Za-z0-9_$]*)"
    r"|(?P<number>\d+(?:'[sS]?[bBoOdDhH][0-9a-fA-F_xXzZ?]+)?)"
    r"|(?P<punct>[()\[\]{},;.:=+*/&|~^!?<>%-])"
)


def lex(text):
    tokens = []
    pos = 0
    while pos < len(text):
        match = TOKEN.match(text, pos)
        if not match:
            raise ValueError(f"Unsupported token at offset {pos}: {text[pos:pos+40]!r}")
        kind, value = match.lastgroup, match.group()
        if kind == "escaped":
            tokens.append(("id", value[1:]))
        elif kind not in ("space", "line", "block"):
            tokens.append((kind, value))
        pos = match.end()
    return tokens


class Reader:
    def __init__(self, text):
        self.tokens = lex(text)
        self.i = 0

    def peek(self, value):
        return self.i < len(self.tokens) and self.tokens[self.i][1] == value

    def take(self, value=None):
        if self.i == len(self.tokens):
            raise ValueError("Unexpected end of netlist")
        token = self.tokens[self.i]
        self.i += 1
        if value is not None and token[1] != value:
            raise ValueError(f"Expected {value!r}, found {token!r}")
        return token

    def name(self):
        token = self.take()
        if token[0] != "id":
            raise ValueError(f"Identifier required, found {token!r}")
        return token[1]

    def expression(self, end):
        result, stack = [], []
        pairs = {"(": ")", "[": "]", "{": "}"}
        while not (not stack and self.peek(end)):
            token = self.take()
            value = token[1]
            if token[0] == "punct" and value in pairs:
                stack.append(pairs[value])
            elif token[0] == "punct" and value in pairs.values():
                if not stack or stack.pop() != value:
                    raise ValueError("Unbalanced expression")
            result.append(token)
        return result

    def parse(self):
        self.take("module")
        module = self.name()
        self.take("(")
        ports = []
        while not self.peek(")"):
            ports.append(self.name())
            if not self.peek(")"):
                self.take(",")
        self.take(")")
        self.take(";")
        declarations, instances, assigns = {}, {}, []
        while not self.peek("endmodule"):
            first = self.name()
            if first in ("input", "output", "inout", "wire"):
                modifiers = []
                while any(self.peek(x) for x in ("wire", "reg", "signed", "unsigned")):
                    modifiers.append(self.name())
                width = []
                if self.peek("["):
                    self.take("[")
                    width = self.expression("]")
                    self.take("]")
                while True:
                    name = self.name()
                    key = first + ":" + name
                    if key in declarations:
                        raise ValueError(f"Duplicate declaration: {key}")
                    declarations[key] = {"kind": first, "name": name,
                                         "modifiers": modifiers, "range": width}
                    if self.peek(";"):
                        self.take(";")
                        break
                    self.take(",")
            elif first == "assign":
                lhs = self.expression("=")
                self.take("=")
                rhs = self.expression(";")
                self.take(";")
                if not lhs or not rhs:
                    raise ValueError("Empty assignment")
                assigns.append({"lhs": lhs, "rhs": rhs})
            else:
                instance = self.name()
                if instance in instances:
                    raise ValueError(f"Duplicate instance: {instance}")
                self.take("(")
                pins = {}
                while not self.peek(")"):
                    self.take(".")
                    pin = self.name()
                    if pin in pins:
                        raise ValueError(f"Duplicate pin: {instance}.{pin}")
                    self.take("(")
                    pins[pin] = self.expression(")")
                    self.take(")")
                    if not self.peek(")"):
                        self.take(",")
                self.take(")")
                self.take(";")
                instances[instance] = {"cell": first, "pins": pins}
        self.take("endmodule")
        if self.i != len(self.tokens):
            raise ValueError("Trailing tokens or multiple modules are unsupported")
        declared_ports = [v["name"] for v in declarations.values() if v["kind"] != "wire"]
        if len(ports) != len(set(ports)) or sorted(ports) != sorted(declared_ports):
            raise ValueError("Header ports and direction declarations do not match uniquely")
        return {"module": module, "ports": sorted(ports), "declarations": declarations,
                "instances": instances, "assigns": sorted(assigns, key=canonical)}, ports


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selfcheck():
    source = r"""module t (a, z); input a; output z; wire \n[0] ;
    arbitrary_cell \i.with/slash  (.A(a), .Z(\n[0] )); assign z = \n[0] ; endmodule"""
    parsed, _ = Reader(source).parse()
    assert parsed["instances"]["i.with/slash"]["pins"]["Z"] == [("id", "n[0]")]
    assert parsed != Reader(source.replace(".A(a)", ".A(z)")).parse()[0]
    assert parsed != Reader(source.replace("arbitrary_cell", "different_cell")).parse()[0]
    try:
        Reader(source.replace("endmodule", "always @(*) z = a; endmodule")).parse()
    except ValueError:
        pass
    else:
        raise AssertionError("Unsupported syntax was silently accepted")
    return {"escaped_identifier_and_nonlibrary_cell": True,
            "pin_change_detected": True, "cell_change_detected": True,
            "unsupported_statement_rejected": True}


def main():
    here = Path(__file__).resolve().parent
    root = here.parents[2]
    original = root / "experiments/20261115_p1_resizer_vs_faeco/arms/Resizer/s382/routed.v"
    reentry = here / "phase0/reentry.v"
    manifest_path = here / "phase0/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    before, before_ports = Reader(original.read_text(encoding="utf-8")).parse()
    after, after_ports = Reader(reentry.read_text(encoding="utf-8")).parse()
    checks = {key: before[key] == after[key] for key in before}
    original_key = str(original.relative_to(root))
    bound = manifest["inputs"][original_key] == sha(original)
    receipt = {
        "scope": "s382 complete exported logical structure; named top-level interface",
        "checker_sha256": sha(Path(__file__)), "manifest_sha256": sha(manifest_path),
        "original": {"path": original_key, "sha256": sha(original)},
        "reentry": {"path": str(reentry.relative_to(root)), "sha256": sha(reentry)},
        "original_matches_manifest": bound, "selfchecks": selfcheck(), "checks": checks,
        "counts": {"ports": len(before["ports"]), "declarations": len(before["declarations"]),
                   "instances": len(before["instances"]),
                   "pin_bindings": sum(len(v["pins"]) for v in before["instances"].values()),
                   "assigns": len(before["assigns"])},
        "port_order_equal": before_ports == after_ports,
        "port_order_original": before_ports, "port_order_reentry": after_ports,
        "canonical_sha256": hashlib.sha256(canonical(before).encode()).hexdigest(),
        "canonical_structure": before,
        "pass": bound and all(checks.values()),
        "limitations": ["No EDA run or equivalence proof; exact named connectivity comparison only.",
                        "Port order change is recorded; positional module instantiation is not equivalent by this check.",
                        "Physical-only cells absent from both Verilog exports are outside this check.",
                        "No placement, routing, DRC, SPEF, library or timing validation is performed here."]}
    target = here / "phase0/STRUCTURE_CHECK.json"
    target.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pass": receipt["pass"], "checks": checks, "counts": receipt["counts"],
                      "port_order_equal": receipt["port_order_equal"]}))
    if not receipt["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
