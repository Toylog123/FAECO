"""Preserve module namespaces while editing the mapped Verilog subset.

Offsets refer to the original text. Comments and quoted attribute values are
masked only for token discovery; their bytes remain intact in every splice.
"""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ModuleSpan:
    name: str
    start: int
    end: int
    text: str


def module_spans(text: str) -> list[ModuleSpan]:
    masked = re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"',
                    lambda m: ''.join('\n' if c=='\n' else ' ' for c in m.group()), text)
    rows=[]
    active=None
    names=set()
    for token in re.finditer(r'\b(?:module|endmodule)\b',masked):
        if token.group()=='module':
            if active is not None:
                raise ValueError('Nested module declaration is unsupported')
            header=re.match(r'\s+(?:automatic\s+)?([A-Za-z_][\w$]*|\\[^\s(]+)',masked[token.end():])
            if header is None:
                raise ValueError('Module name unavailable')
            name=header.group(1)
            if name in names:
                raise ValueError(f'Duplicate module definition: {name}')
            names.add(name)
            active=(name,token.start())
        elif active is None:
            raise ValueError('endmodule without matching module')
        else:
            name,start=active
            rows.append(ModuleSpan(name,start,token.end(),text[start:token.end()]))
            active=None
    if active is not None:
        raise ValueError('Unterminated module declaration')
    return rows


def target_module_text(text: str, name: str) -> str:
    for span in module_spans(text):
        if span.name==name:
            return span.text
    raise ValueError(f'Target module unavailable: {name}')


def select_top_module(text: str, requested: str | None = None) -> str:
    """Select a unique source root before injecting library model definitions.

    This supports the mapped, non-parameterized instance subset. Ambiguity
    requires the caller to name its source module; library roots are never
    eligible to become the object of a full-netlist proof.
    """
    from .gate_sizing import _mapped_code
    names = {span.name for span in module_spans(text)}
    if requested is not None:
        if requested not in names:
            raise ValueError(f'Requested proof top is not a source module: {requested}')
        return requested
    instantiated = set()
    pattern = r'(?<![\w$\\])([A-Za-z_$][\w$]*|\\[^\s]+)\s+(?:[A-Za-z_$][\w$]*|\\[^\s]+)\s*\('
    for match in re.finditer(pattern, _mapped_code(text)):
        if match.group(1) in names:
            instantiated.add(match.group(1))
    roots = names - instantiated
    if len(roots) != 1:
        raise ValueError('A unique source top is required; specify top_module explicitly')
    return next(iter(roots))


def replace_target_module(text: str, name: str, replacement: str) -> str:
    new=module_spans(replacement)
    if len(new)!=1 or new[0].name!=name:
        raise ValueError('Replacement must contain exactly the target module')
    for span in module_spans(text):
        if span.name==name:
            return text[:span.start]+new[0].text+text[span.end:]
    raise ValueError(f'Target module unavailable: {name}')
