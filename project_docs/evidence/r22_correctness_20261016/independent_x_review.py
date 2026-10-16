"""Independent whole-token X isolation audit of the four archived B2 raws.

This evidence checker does not import the production parser or primary
x_identity_certificate API, invoke EDA, or modify the reviewed netlists.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SCOPE = HERE / "B2_X_SCOPE_CHECK.json"
LEXER = re.compile(
    r"(?P<COMMENT>//[^\n]*|/\*.*?\*/)"
    r'|(?P<STRING>"(?:\\.|[^"\\])*")'
    r"|(?P<NUMBER>(?:\d[\d_]*\s*)?'[sS]?[bBoOdDhH][0-9a-fA-F_xXzZ?]+|'[01xXzZ])"
    r"|(?P<ESC>\\[^\s]+)|(?P<ID>[A-Za-z_$][A-Za-z0-9_$]*)"
    r"|(?P<INT>\d[\d_]*)|(?P<SYMBOL>\S)", re.S)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identifier(value):
    return value[1:] if value.startswith("\\") else value


def scan(text, top):
    tokens = [(match.lastgroup, match.group(), match.start(), match.end())
              for match in LEXER.finditer(text) if match.lastgroup != "COMMENT"]
    if any(kind == "STRING" or value == "`" for kind, value, _, _ in tokens):
        raise ValueError("Unsupported string/preprocessor syntax in mapped audit domain")
    occurrences = {}
    for index, token in enumerate(tokens):
        if token[0] in {"ID", "ESC"}:
            occurrences.setdefault(identifier(token[1]), set()).add(index)
    declarations, header, x_sources = {}, {}, {}
    index = 0
    seen_module = ended = False
    while index < len(tokens):
        first = tokens[index][1]
        if first == "endmodule":
            if ended or not seen_module:
                raise ValueError("Unexpected endmodule")
            ended = True
            index += 1
            continue
        if ended:
            raise ValueError("Extra modules/statements outside the selected top")
        stop = next((i for i in range(index, len(tokens)) if tokens[i][1] == ";"), None)
        if stop is None:
            raise ValueError("Unterminated mapped statement")
        values = [token[1] for token in tokens[index:stop]]
        raw = text[tokens[index][2]:tokens[stop][3]]
        if first == "module":
            if seen_module or values[1] != top or values[2] != "(" or values[-1] != ")":
                raise ValueError("Non-unique/non-simple target module header")
            ports = values[3:-1]
            if any(value != "," and tokens[index + 3 + offset][0] not in {"ID", "ESC"} for offset, value in enumerate(ports)):
                raise ValueError("Unsupported ANSI/complex module ports")
            for offset, value in enumerate(ports):
                if value != ",":
                    name = identifier(value)
                    if name in header:
                        raise ValueError("Duplicate port")
                    header[name] = index + 3 + offset
            seen_module = True
        elif first in {"wire", "input", "output", "inout"}:
            pos = 1
            signed = False
            if pos < len(values) and values[pos] in {"signed", "unsigned"}:
                signed = values[pos] == "signed"
                pos += 1
            width = 1
            if pos < len(values) and values[pos] == "[":
                dimensions = values[pos:pos + 5]
                if len(dimensions) != 5 or dimensions[2] != ":" or dimensions[4] != "]" or not dimensions[1].isdigit() or not dimensions[3].isdigit():
                    raise ValueError("Unsupported mapped declaration dimensions")
                width = abs(int(dimensions[1]) - int(dimensions[3])) + 1
                pos += 5
            names = values[pos:]
            if not names:
                raise ValueError("Empty declaration")
            for offset, value in enumerate(names):
                if offset % 2:
                    if value != ",":
                        raise ValueError("Unsupported declaration initializer/array")
                else:
                    if tokens[index + pos + offset][0] not in {"ID", "ESC"}:
                        raise ValueError("Unsupported declaration net")
                    declarations.setdefault(identifier(value), []).append({"role": first, "width": width, "signed": signed,
                        "raw": raw, "token_index": index + pos + offset})
        elif first == "assign":
            numbers = [token for token in tokens[index:stop] if token[0] == "NUMBER" and re.search(r"[xXzZ?]", token[1].split("'")[-1])]
            if numbers:
                if len(values) != 4 or values[2] != "=" or tokens[index + 1][0] not in {"ID", "ESC"}:
                    raise ValueError("Non-isolated X/Z literal assignment")
                literal = re.fullmatch(r"(\d+)'[sS]?[bBoOdDhH]([xX_]+)", values[3])
                if literal is None or int(literal.group(1)) <= 0:
                    raise ValueError("X/Z assignment is not an explicit sized all-X constant")
                name = identifier(values[1])
                if name in x_sources:
                    raise ValueError("Multiple X drivers")
                x_sources[name] = {"lhs": name, "rhs": values[3], "width": int(literal.group(1)),
                                       "raw": raw, "lhs_token": index + 1}
        elif first.startswith("sky130_fd_sc_hd__"):
            # Every identifier in the complete instance body remains in the
            # occurrence table, including concatenations, selects and escapes.
            if len(values) < 4 or values[2] != "(" or values[-1] != ")":
                raise ValueError("Unsupported mapped SKY instance")
        else:
            raise ValueError(f"Unsupported mapped statement kind: {first}")
        index = stop + 1
    if not seen_module or not ended:
        raise ValueError("Incomplete target module")
    isolated = []
    for name, source in x_sources.items():
        decl = declarations.get(name, [])
        if not decl or any(d["role"] in {"input", "inout"} or d["width"] != source["width"] for d in decl):
            raise ValueError(f"X source width/role not isolated: {name}")
        roles = Counter(d["role"] for d in decl)
        output = roles.get("output", 0) == 1
        if roles != Counter({"wire": 1, **({"output": 1} if output else {})}) or (name in header) != output:
            raise ValueError(f"X net declarations/port identity ambiguous: {name}")
        allowed = {source["lhs_token"], *(d["token_index"] for d in decl)}
        if output:
            allowed.add(header[name])
        unexpected = occurrences[name] - allowed
        if unexpected:
            locations = [text.count("\n", 0, tokens[i][2]) + 1 for i in sorted(unexpected)]
            raise ValueError(f"X source has another use/driver at lines {locations}: {name}")
        isolated.append({"lhs": name, "rhs": source["rhs"], "width": source["width"], "assign": source["raw"],
                         "declarations": [{k: value for k, value in d.items() if k != "token_index"} for d in decl],
                         "direct_top_output": output, "whole_identifier_token_occurrences": len(occurrences[name])})
    return {"top": top, "ordered_ports": list(header), "isolated_x_sources": isolated}


def main():
    scope = json.loads(SCOPE.read_text(encoding="utf-8"))
    before = {str(SCOPE.relative_to(ROOT)): digest(SCOPE), str(Path(__file__).resolve().relative_to(ROOT)): digest(__file__)}
    reviewed = []
    core_text = None
    for pair in scope["pairs"]:
        sides = []
        for side in pair["sides"]:
            path = ROOT / side["path"]
            actual_hash = digest(path)
            assert actual_hash == side["sha256"], (path, "raw hash differs from source certificate")
            before[str(path.relative_to(ROOT))] = actual_hash
            text = path.read_text(encoding="utf-8")
            analysis = scan(text, pair["top_module"])
            assert len(analysis["isolated_x_sources"]) == side["explicit_x_literal_count"]
            sides.append({"path": str(path.relative_to(ROOT)), "sha256": actual_hash, "analysis": analysis})
            if pair["top_module"] == "picorv32" and core_text is None:
                core_text = text
        assert sides[0]["analysis"] == sides[1]["analysis"], "X assignment/declaration/port identity changed"
        reviewed.append({"top": pair["top_module"], "same_identity_and_no_other_tokens": True, "sides": sides})
    probes = {}
    for name, insertion in {
        "concat_select_consumer": "assign dummy = {trace_data[0],1'b0};",
        "escaped_select_consumer": "assign dummy = \\cpuregs[0] [0];",
        "escaped_simple_name_consumer": "assign dummy = \\trace_data [0];",
        "escaped_simple_alias_consumer": "assign dummy = \\decoded_rs [0];",
        "alias_consumer": "wire dummy; assign dummy = decoded_rs[0];",
        "additional_partial_driver": "assign trace_data[1] = 1'b0;",
        "behavioral_consumer": "always @* dummy = trace_data[0];",
        "new_x_source": "assign dummy = 1'bx;",
    }.items():
        try:
            scan(core_text.replace("endmodule", insertion + "\nendmodule"), "picorv32")
        except ValueError as error:
            probes[name] = {"rejected": True, "reason": str(error)}
        else:
            raise AssertionError(f"Independent whole-token checker missed {name}")
    after = {name: digest(ROOT / name) for name in before}
    assert before == after, "Reviewed source changed during check"
    result = {"schema": "independent-B2-X-token-review-v1", "eda_executed": False, "production_imported": False,
              "inputs_and_checker_sha256": before, "source_stable": True, "pairs": reviewed, "negative_probes": probes,
              "limit": "Exact constant-X identity/isolation only; remaining functional/state equivalence and all library semantics need separately bound proof."}
    (HERE / "B2_X_INDEPENDENT_REVIEW.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pairs": len(reviewed), "negative_probes": len(probes), "source_stable": True, "eda_executed": False}))


if __name__ == "__main__":
    main()
