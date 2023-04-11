"""Custom Pygments tools for working with OpenQASM 2."""

__all__ = ["OpenQASM2Lexer"]

import re

from pygments import token
from pygments.lexer import RegexLexer, words

# OQ 2 uses a more restrictive identifier format than OQ 3.
_IDENTIFIER = "[a-z][A-Za-z0-9_]*"
_REAL = r"([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)([eE][-+]?[0-9]+)?"
_INTEGER = "(0|[1-9][0-9]*)"


class OpenQASM2Lexer(RegexLexer):
    """A custom lexer for highlighting OpenQASM 2 code with Pygments.

    This registers itself with the Pygments aliases ``qasm2`` and ``openqasm2``, and associates
    itself with file names ending in ``.qasm``."""

    name = "OpenQASM 2"
    aliases = ["openqasm2", "qasm2"]
    filenames = ["*.qasm"]
    flags = re.MULTILINE

    tokens = {
        "root": [
            (r"[ \r\n\t]+", token.Whitespace),
            (r"\bOPENQASM\b", token.Comment.Preproc, "version"),
            (r"//.*$", token.Comment.Single),
            (r"\binclude\b", token.Keyword.Namespace, "include"),
            (
                words("def gate opaque".split(), prefix="\\b", suffix="\\b"),
                token.Keyword.Declaration,
                "callable",
            ),
            (
                words("qreg creg".split(), prefix="\\b", suffix="\\b"),
                token.Keyword.Type,
            ),
            (words("U CX".split(), prefix="\\b", suffix="\\b"), token.Name.Builtin),
            (
                words("sin cos tan exp ln sqrt".split(), prefix="\\b", suffix="\\b"),
                token.Name.Builtin,
            ),
            (
                words("reset measure barrier".split(), prefix="\\b", suffix="\\b"),
                token.Operator.Word,
            ),
            (r"\bif\b", token.Keyword),
            (r"\bpi\b", token.Name.Constant),
            (words("[ ] { } ( ) , : ;".split()), token.Punctuation),
            (words("== -> + - * / ^".split()), token.Operator),
            (_INTEGER, token.Number),
            (_REAL, token.Number.Float),
            # Preferentially tokenise identifiers that are used in calling contexts (gates and
            # functions) as callables.  Since we use the same highlighting for gates and functions,
            # it doesn't matter that we'll tokenise (e.g.) the identifier in `rz(...)` with the
            # function rule not the gate one.
            (_IDENTIFIER + rf"(?=[ \r\n\t]+{_IDENTIFIER})", token.Name.Function),
            (_IDENTIFIER + r"(?=[ \r\n\t]*\()", token.Name.Function),
            (_IDENTIFIER, token.Name),
        ],
        # Handle the restricted format for version numbers.  The original paper is a little
        # inconsistent here - the text says it must be "major.minor", the BNF grammar at the end
        # says it can be any valid real.  We compromise to something more sensible.
        "version": [
            (r"[ \r\n\t]+", token.Whitespace),
            (r"\d+(\.\d+)?", token.Literal),
            (";", token.Punctuation, "#pop"),
        ],
        # Tokenise include statements that have a special string-literal type.
        "include": [
            (r"[ \r\n\t]+", token.Whitespace),
            (r'"[^"]*"', token.String, "#pop"),
            (r"'[^']*'", token.String, "#pop"),
        ],
        # Require that the next object is an identifier, and tokenise it as a callable.
        "callable": [
            (r"[ \r\n\t]+", token.Whitespace),
            (_IDENTIFIER, token.Name.Function, "#pop"),
        ],
    }
