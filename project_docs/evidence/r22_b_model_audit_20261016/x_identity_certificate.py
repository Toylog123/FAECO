"""Read-only, fail-closed isolation certificate for explicit constant-X sources.

This does not prove equivalence, reset behavior, or arbitrary four-state logic.
It permits removing only identical, unconsumed X sources from a separate
two-state comparison. Callers must independently validate/elaborate cell models,
reject unsupported Z semantics, and bind the exact input bytes and this file hash.
Supported syntax: non-ANSI modules, wire/input/output declarations, continuous
assignments, and unparameterized named-port instances. Other syntax is rejected.
Only comments/whitespace are normalized; escaped identifiers are lexed atomically.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import re

_TOKEN = re.compile(
    r"(?P<space>\s+)|(?P<line>//[^\n]*)|(?P<block>/\*.*?\*/)"
    r"|(?P<escaped>\\[^\s]+)"
    r"|(?P<literal>(?:[0-9][0-9_]*\s*)?'[sS]?[bBoOdDhH][0-9a-fA-FxXzZ?_]+|'[01xXzZ])"
    r"|(?P<id>[A-Za-z_$][A-Za-z0-9_$]*)|(?P<number>[0-9][0-9_]*)"
    r"|(?P<op>===|!==|<<<|>>>|==|!=|<=|>=|&&|\|\||<<|>>|\*\*|~\^|\^~|[;,:.()\[\]{}=+*/%&|^~!<>?\-])",
    re.S,
)
_ID = re.compile(r"(?:[A-Za-z_$][A-Za-z0-9_$]*|\\[^\s]+)\Z")
_LITERAL = re.compile(r"(?:[0-9][0-9_]*\s*)?'[sS]?[bBoOdDhH]([0-9a-fA-FxXzZ?_]+)\Z|'([01xXzZ])\Z")
_RESERVED = set(('module endmodule input output wire signed unsigned inout reg tri '
                 'always initial generate endgenerate begin end if else case endcase '
                 'parameter localparam function endfunction task endtask assign '
                 'buf not and nand or nor xor xnor tran rtran bufif0 bufif1 notif0 notif1').split())
_BINARY = set('+ - * / % & | ^ ~^ ^~ && || == != === !== < > <= >= << >> <<< >>> **'.split())
_UNARY = {'+', '-', '!', '~', '&', '|', '^', '~^', '^~'}


def _fail(message):
    raise ValueError(message)


def _name(token):
    if not _ID.fullmatch(token) or token in _RESERVED:
        _fail('expected identifier: ' + token)
    return token[1:] if token.startswith('\\') else token


def _lex(text):
    tokens = []
    position = 0
    while position < len(text):
        match = _TOKEN.match(text, position)
        if match is None:
            _fail('unsupported lexical syntax at offset ' + str(position))
        if match.lastgroup == 'literal':
            literal = re.sub(r'\s|_', '', match.group()).lower()
            based = re.fullmatch(r"([0-9]*)'s?([bodh])([0-9a-fxz?]+)", literal)
            if based:
                width, base, digits = based.groups()
                valid = {'b': '01xz?', 'o': '01234567xz?',
                         'd': '0123456789xz?', 'h': '0123456789abcdefxz?'}[base]
                if (width and int(width) == 0) or not set(digits) <= set(valid):
                    _fail('invalid based literal')
                if base == 'd' and set(digits) & set('xz?') and (len(digits) != 1):
                    _fail('unsupported decimal unknown literal')
        if match.lastgroup not in {'space', 'line', 'block'}:
            tokens.append(match.group())
        position = match.end()
    return tokens


def _literal_bits(token):
    match = _LITERAL.fullmatch(token)
    return (match.group(1) or match.group(2)).replace('_', '').lower() if match else ''


def _expression(tokens, *, lvalue=False):
    """Recognize a bounded expression grammar; never ignore unexplained tokens."""
    index = 0

    def take(expected):
        nonlocal index
        if index >= len(tokens) or tokens[index] != expected:
            _fail('unsupported expression, expected ' + expected)
        index += 1

    def expr():
        nonlocal index
        atom()
        while not lvalue and index < len(tokens) and tokens[index] in _BINARY:
            index += 1
            atom()
        if not lvalue and index < len(tokens) and tokens[index] == '?':
            index += 1
            expr()
            take(':')
            expr()

    def atom():
        nonlocal index
        if index >= len(tokens):
            _fail('empty expression')
        token = tokens[index]
        index += 1
        if token in _UNARY and not lvalue:
            atom()
        elif token == '(' and not lvalue:
            expr()
            take(')')
        elif token == '{':
            expr()
            if not lvalue and index < len(tokens) and tokens[index] == '{':
                index += 1
                expr()
                while index < len(tokens) and tokens[index] == ',':
                    index += 1
                    expr()
                take('}')
            else:
                while index < len(tokens) and tokens[index] == ',':
                    index += 1
                    expr()
            take('}')
        elif lvalue or not (_LITERAL.fullmatch(token) or re.fullmatch(r'[0-9][0-9_]*', token)):
            _name(token)
        while index < len(tokens) and tokens[index] == '[':
            index += 1
            # Lvalue selects accept only constant integer bounds; elaborated
            # variable/parameterized selects are outside this certificate.
            if lvalue:
                if index >= len(tokens) or not re.fullmatch(r'[0-9][0-9_]*', tokens[index]):
                    _fail('unsupported lvalue select')
                index += 1
            else:
                expr()
            if index < len(tokens) and tokens[index] == ':':
                index += 1
                if lvalue:
                    if index >= len(tokens) or not re.fullmatch(r'[0-9][0-9_]*', tokens[index]):
                        _fail('unsupported lvalue select bound')
                    index += 1
                else:
                    expr()
            take(']')

    expr()
    if index != len(tokens):
        _fail('unconsumed expression syntax: ' + ' '.join(tokens[index:]))


def _scan(text):
    tokens = _lex(text)
    modules = {}
    source_records = []
    instantiated = set()
    i = 0

    def take(expected):
        nonlocal i
        if i >= len(tokens) or tokens[i] != expected:
            _fail('expected ' + expected)
        i += 1

    while i < len(tokens):
        take('module')
        module = _name(tokens[i]); i += 1
        if module in modules:
            _fail('duplicate module ' + module)
        take('(')
        ports = {}
        while tokens[i] != ')':
            name = _name(tokens[i])
            if name in ports:
                _fail('duplicate module port ' + name)
            ports[name] = i; i += 1
            if tokens[i] != ')':
                take(',')
                if tokens[i] == ')':
                    _fail('trailing module port comma')
        take(')'); take(';')
        start = i
        declarations = {}
        permitted = {}
        sources = {}
        while i < len(tokens) and tokens[i] != 'endmodule':
            begin = i
            while i < len(tokens) and tokens[i] != ';':
                if tokens[i] in {'module', 'endmodule'}:
                    _fail('missing statement semicolon')
                i += 1
            if i >= len(tokens):
                _fail('unterminated statement')
            statement = tokens[begin:i]; i += 1
            if not statement:
                _fail('empty statement')
            kind = statement[0]
            if kind in {'wire', 'input', 'output'}:
                j = 1
                prefix = []
                if j < len(statement) and statement[j] == 'wire':
                    if kind == 'wire':
                        _fail('duplicate wire qualifier')
                    prefix.append('wire'); j += 1
                if j < len(statement) and statement[j] in {'signed', 'unsigned'}:
                    prefix.append(statement[j]); j += 1
                if j < len(statement) and statement[j] == '[':
                    # Explicit integer bounds only: parameterized widths are unsupported.
                    width = statement[j:j+5]
                    if len(width) != 5 or width[2] != ':' or width[4] != ']' or not all(re.fullmatch(r'[0-9][0-9_]*', width[k]) for k in (1,3)):
                        _fail('unsupported declaration width')
                    prefix.extend(width); j += 5
                while j < len(statement):
                    name = _name(statement[j])
                    declarations.setdefault(name, []).append((kind, tuple(prefix)))
                    permitted.setdefault(name, set()).add(begin+j)
                    j += 1
                    if j < len(statement):
                        if statement[j] != ',' or j+1 == len(statement):
                            _fail('unsupported declaration suffix')
                        j += 1
            elif kind == 'assign':
                if statement.count('=') != 1:
                    _fail('unsupported continuous assign')
                eq = statement.index('=')
                _expression(statement[1:eq], lvalue=True); _expression(statement[eq+1:])
                x_positions = [k for k,t in enumerate(statement) if 'x' in _literal_bits(t)]
                if x_positions:
                    if len(statement) != 4 or eq != 2 or x_positions != [3] or set(_literal_bits(statement[3])) != {'x'}:
                        _fail('X must be the entire scalar/vector constant RHS of one net assign')
                    name = _name(statement[1])
                    if name in sources:
                        _fail('duplicate X source assignment ' + name)
                    sources[name] = tuple(statement)
                    permitted.setdefault(name, set()).add(begin+1)
                elif any(_literal_bits(t) and (set(_literal_bits(t)) & {'z', '?'}) for t in statement):
                    _fail('Z/wildcard literal outside certificate scope')
            else:
                # Exactly one named-port instance; positional, arrays, parameters,
                # primitives, procedural blocks and unknown statements fail closed.
                cell = _name(statement[0]); _name(statement[1])
                instantiated.add(cell)
                if statement[2:3] != ['('] or statement[-1:] != [')']:
                    _fail('unsupported instance statement')
                j = 3
                seen_pins = set()
                while j < len(statement)-1:
                    if statement[j] != '.':
                        _fail('expected named cell pin')
                    pin = _name(statement[j+1])
                    if pin in seen_pins:
                        _fail('duplicate cell pin')
                    seen_pins.add(pin)
                    if statement[j+2] != '(':
                        _fail('expected cell pin connection')
                    j += 3
                    connection_start = j
                    depth = 1
                    while j < len(statement) and depth:
                        depth += (statement[j] == '(') - (statement[j] == ')')
                        j += 1
                    if depth:
                        _fail('unbalanced cell connection')
                    connection = statement[connection_start:j-1]
                    if connection:
                        _expression(connection)
                    if any(set(_literal_bits(t)) & {'x','z','?'} for t in connection):
                        _fail('non-assign X/Z cell connection')
                    if j < len(statement)-1:
                        if statement[j] != ',' or j+1 == len(statement)-1:
                            _fail('unsupported cell connection separator')
                        j += 1
                if j != len(statement)-1:
                    _fail('unconsumed instance syntax')
        stop = i
        take('endmodule')
        for name, assignment in sources.items():
            decls = declarations.get(name, [])
            if not decls or any(kind == 'input' for kind,_ in decls):
                _fail('X source must have an explicit wire/output declaration: ' + name)
            kinds = [kind for kind,_ in decls]
            if any(count > 1 for count in Counter(kinds).values()):
                _fail('duplicate X net declaration: ' + name)
            is_output = 'output' in kinds
            if (name in ports) != is_output:
                _fail('X source module port/declaration role mismatch: ' + name)
            allowed = set(permitted.get(name, set()))
            if is_output:
                allowed.add(ports[name])
            # Count identifiers as lexical atoms, including escaped simple names.
            for index in range(start, stop):
                token = tokens[index]
                if _ID.fullmatch(token) and (token[1:] if token.startswith('\\') else token) == name and index not in allowed:
                    _fail('X source has consumer/extra use: ' + module + '.' + name)
            source_records.append({'module': module, 'lhs': name,
                'assignment_tokens': list(assignment),
                'declarations': [[kind,list(prefix)] for kind,prefix in sorted(decls)],
                'port_role': 'output' if is_output else 'internal_wire',
                'consumer_count': 0})
        modules[module] = {'sources': list(sources)}
    if not modules:
        _fail('no supported module')
    for source in source_records:
        if source['port_role'] == 'output' and source['module'] in instantiated:
            _fail('X helper output may escape through a module instance')
    return sorted(source_records, key=lambda row: (row['module'],row['lhs']))


def certify_pair(goldtext: str, gatetext: str) -> dict:
    """Return JSON-compatible certificate; ``certified=False`` on any unknown.

    Hashes bind precisely the UTF-8 encoding of strings supplied by the caller;
    callers separately bind original file byte hashes (including newline form).
    """
    result = {'schema': 'r22-isolated-X-identity-v1', 'certified': False,
              'scope': 'explicit isolated constant-X identity only; not equivalence',
              'sources': []}
    if not isinstance(goldtext,str) or not isinstance(gatetext,str):
        result['reason'] = 'both inputs must be str'
        return result
    result['gold_text_utf8_sha256'] = hashlib.sha256(goldtext.encode('utf-8')).hexdigest()
    result['gate_text_utf8_sha256'] = hashlib.sha256(gatetext.encode('utf-8')).hexdigest()
    try:
        gold, gate = _scan(goldtext), _scan(gatetext)
        if gold != gate:
            _fail('X source assignments/declarations/module/port roles differ')
    except (ValueError, IndexError, RecursionError) as exc:
        result['reason'] = str(exc) or type(exc).__name__
        return result
    result.update(certified=True, reason='all explicit X sources are identical and isolated' if gold else 'no explicit X literals in supported syntax', sources=gold)
    return result
