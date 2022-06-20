"""Custom lexer for OpenPulse."""

__all__ = ["OpenPulseLexer"]

import re
from typing import List

from pygments import token
from pygments.lexer import RegexLexer, words

from . import _lexeme


class OpenPulseLexer(RegexLexer):
    """A Pygments lexer for the OpenPulse pulse-calibration dialect used with OpenQASM 3.

    This registers itself with the Pygments alias ``openpulse``."""

    name = "OpenPulse"
    aliases = ["openpulse"]
    filenames: List[str] = []
    flags = re.MULTILINE | re.UNICODE

    tokens = {
        "root": [
            (r"[ \r\n\t]+", token.Whitespace),
            (r"\bextern\b", token.Keyword.Type),
            (r"\breturn\b", token.Keyword),
            (
                words(
                    (
                        "port waveform frame bool bit int uint float angle complex array duration"
                        " stretch"
                    ).split(),
                    prefix="\\b",
                    suffix="\\b",
                ),
                token.Keyword.Type,
            ),
            (r"//.*$", token.Comment.Single),
            (r"/\*", token.Comment.Multiline, "comment"),
            (words("pi euler tau π τ ℇ".split(), prefix="\\b", suffix="\\b"), token.Name.Constant),
            (
                words("delay barrier".split(), prefix="\\b", suffix="\\b"),
                token.Operator.Word,
            ),
            (
                words(
                    (
                        "durationof sizeof arccos arcsin arctan ceiling cos exp floor log mod"
                        " popcount rotl rotr sin sqrt tan"
                    ).split(),
                    prefix="\\b",
                    suffix="\\b",
                ),
                token.Name.Builtin,
            ),
            (
                words(
                    (
                        "play capture newframe set_phase shift_phase get_phase set_frequency"
                        " shift_frequency get_frequency mix sum phase_shift scale"
                    ).split(),
                    prefix="\\b",
                    suffix="\\b",
                ),
                token.Name.Builtin,
            ),
            (words("[ ] { } ( ) , : ;".split()), token.Punctuation),
            (
                words(
                    (
                        "== != += -= *= /= &= |= ~= ^= <<= >>= %= **= = -> ++ + - ** * / % || | &&"
                        " & ^ @ ~ ! >= >> > <= << <"
                    ).split()
                ),
                token.Operator,
            ),
            # Numeric literal tokens.  These are in a particular order, because Pygments will try
            # the rules from top to bottom, and there are potential ambiguities.  Duration and
            # imaginary literals are parsed into the `float` rules, because Pygments doesn't have an
            # alternative token for them.
            (r"0[bB]([01]_?)*[01]", token.Number.Bin),
            (r'"([01]_?)*[01]"', token.Number.Bin),  # Bitstrings.
            (r"0o([0-7]_?)*[0-7]", token.Number.Oct),
            (r"0[xX]([0-9a-fA-F]_?)*[0-9a-fA-F]", token.Number.Hex),
            (
                rf"{_lexeme.DECIMAL_LITERAL}{_lexeme.FLOAT_EXPONENT}({_lexeme.FLOAT_SUFFIX})?",
                token.Number.Float,
            ),
            (
                rf"\.{_lexeme.DECIMAL_LITERAL}({_lexeme.FLOAT_EXPONENT})?({_lexeme.FLOAT_SUFFIX})?",
                token.Number.Float,
            ),
            (
                rf"{_lexeme.DECIMAL_LITERAL}\.({_lexeme.DECIMAL_LITERAL})?"
                rf"({_lexeme.FLOAT_EXPONENT})?({_lexeme.FLOAT_SUFFIX})?",
                token.Number.Float,
            ),
            (f"{_lexeme.DECIMAL_LITERAL}{_lexeme.FLOAT_SUFFIX}", token.Number.Float),
            (_lexeme.DECIMAL_LITERAL, token.Number),
            # Hardware qubits.
            (r"\$[0-9]+", token.Literal),
            # Lookahead lexing of things that look like callables.
            (_lexeme.IDENTIFIER + r"(?=[ \r\n\t]*\()", token.Name.Function),
            # OpenPulse allows general identifiers with a proceeding `$`.
            (rf"\$?{_lexeme.IDENTIFIER}", token.Name),
        ],
        # Handle multiline comments.
        "comment": [
            (r"[^*/]+", token.Comment.Multiline),
            (r"/\*", token.Comment.Multiline, "#push"),
            (r"\*/", token.Comment.Multiline, "#pop"),
            (r"[*/]", token.Comment.Multiline),
        ],
    }
