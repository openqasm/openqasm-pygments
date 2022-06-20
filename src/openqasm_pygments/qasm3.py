"""Custom Pygments tools for working with OpenQASM 3."""

__all__ = ["OpenQASM3Lexer"]

import re
import warnings
from typing import Union, Mapping, Optional, Sequence, Tuple

from pygments import token
from pygments.lexer import Lexer, RegexLexer, words, include
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from . import _lexeme
from .exceptions import LexerWarning


class OpenQASM3Lexer(RegexLexer):
    """A custom lexer for highlighting OpenQASM 3 code with Pygments.

    This registers itself as the Pygments aliases ``qasm3`` and ``openqasm3``, and associates itself
    with filenames ending in ``.qasm``."""

    name = "OpenQASM 3"
    aliases = ["openqasm3", "qasm3"]
    filenames = ["*.qasm"]
    flags = re.MULTILINE | re.UNICODE

    def __init__(
        self,
        default_pulse_lexer: Union[str, Lexer, None] = None,
        *,
        infer_pulse_grammar: bool = True,
        pulse_lexer_overrides: Optional[Mapping[str, Lexer]] = None,
        **options,
    ):
        """
        :param default_pulse_lexer: The default lexer to use if no ``defcalgrammar`` statements are
            read.  This can be either a Pygments lexer alias as a string (e.g. ``"openpulse"``), or
            an instance of a Pygments lexer.  If ``infer_pulse_grammar`` is ``True``, the given
            lexer will be overridden if a ``defcalgrammar`` statement is encounted whose value is
            not a compatible alias.
        :type default_pulse_lexer: Union[str, pygments.lexer.Lexer, None]

        :param infer_pulse_grammar: If set to ``True`` (default), then any ``defcalgrammar``
            statements encountered during a run will be parsed for their value.  This value will be
            treated as a Pygments lexer alias, and used to find a lexer for any pulse blocks.
        :type infer_pulse_grammar: bool

        :param pulse_lexer_overrides: Mapping of string aliases to Pygments lexers.  This mapping is
            used to provide specific overrides for different ``defcalgrammar`` statements; if the
            value is in this mapping, the given lexer will be used verbatim instead of using the
            Pygments alias machinery to find a lexer instance.  This will not be used if
            ``infer_pulse_grammar`` is ``False``.
        :type pulse_lexer_overrides: Mapping[str, pygments.lexer.Lexer]
        """
        # We have to store the general options so we can pass them on to the sublexer we use for
        # defcalgrammar statements, if given an alias, or if we infer.
        self.__options = options
        self.__default_defcal_lexer = default_pulse_lexer
        self.__defcal_lexer: Union[str, Lexer, None] = None
        self.__pulse_lexer_overrides = pulse_lexer_overrides if pulse_lexer_overrides else {}
        self.infer_pulse_grammar = infer_pulse_grammar
        super().__init__(**options)

    def _defcalgrammar_callback(self, match):
        text = match.group(0)
        alias = text[1:-1]
        if self.infer_pulse_grammar and not (
            isinstance(self.__defcal_lexer, Lexer) and alias.lower() in self.__defcal_lexer.aliases
        ):
            self.__defcal_lexer = alias
        yield match.start(), token.Literal.String, text

    tokens = {
        "root": [
            (r"^[ \t]*#?pragma", token.Comment.Preproc, "pragma"),
            (r"^[ \t]*@\w+", token.Name.Decorator, "annotation"),
            (r"[ \r\n\t]+", token.Whitespace),
            (r"\bOPENQASM\b", token.Comment.Preproc, "version"),
            (r"//.*$", token.Comment.Single),
            (r"/\*", token.Comment.Multiline, "comment"),
            (r"\binclude\b", token.Keyword.Namespace, "include"),
            (r"\bdefcalgrammar\b", token.Keyword.Namespace, "defcalgrammar"),
            (
                words("def gate extern".split(), prefix="\\b", suffix="\\b"),
                token.Keyword.Declaration,
                "callable",
            ),
            ("cal", token.Keyword, "cal prelude"),
            ("defcal", token.Keyword.Declaration, ("cal prelude", "callable")),
            ("let", token.Keyword.Declaration),
            (
                words(
                    "break continue end if else for while box return in".split(),
                    prefix="\\b",
                    suffix="\\b",
                ),
                token.Keyword,
            ),
            (
                words("input output readonly mutable const".split(), prefix="\\b", suffix="\\b"),
                token.Keyword.Type,
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
                    "qreg qubit creg bool bit int uint float angle complex array duration stretch".split(),
                    prefix="\\b",
                    suffix="\\b",
                ),
                token.Keyword.Type,
            ),
            (words("gphase U".split(), prefix="\\b", suffix="\\b"), token.Name.Builtin),
            (words("pi euler tau π τ ℇ".split(), prefix="\\b", suffix="\\b"), token.Name.Constant),
            (words("inv ctrl negctrl pow".split(), prefix="\\b", suffix="\\b"), token.Name.Builtin),
            (
                words("delay reset measure barrier".split(), prefix="\\b", suffix="\\b"),
                token.Operator.Word,
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
            ("#dim", token.Name.Attribute),
            # Preferentially tokenise identifiers that are used in calling contexts (gates and
            # functions) as callables.  Since we use the same highlighting for gates and functions,
            # it doesn't matter that we'll tokenise (e.g.) the identifier in `rz(...)` with the
            # function rule not the gate one.
            (_lexeme.IDENTIFIER + r"(?=[ \r\n\t]+in\b)", token.Name),  # Skip the loop variable.
            (_lexeme.IDENTIFIER + rf"(?=[ \r\n\t]+{_lexeme.IDENTIFIER})", token.Name.Function),
            (_lexeme.IDENTIFIER + r"(?=[ \r\n\t]*\()", token.Name.Function),
            # Identifiers.
            (_lexeme.IDENTIFIER, token.Name),
        ],
        "version": [
            (r"[ \r\n\t]+", token.Whitespace),
            (r"//.*$", token.Comment.Single),
            (r"/\*", token.Comment.Multiline, "comment"),
            (r"\d+(\.\d+)?", token.Literal),
            (";", token.Punctuation, "#pop"),
        ],
        "annotation": [
            (r"[^\n]+", token.Text),
            (r"\n", token.Whitespace, "#pop"),
        ],
        "pragma": [
            (r"[^\n]+", token.Text),
            (r"\n", token.Whitespace, "#pop"),
        ],
        # Require that the next token is an identifier, and tokenise it as a callable identifier.
        "callable": [
            (r"[ \r\n\t]+", token.Whitespace),
            (r"//.*$", token.Comment.Single),
            (r"/\*", token.Comment.Multiline, "comment"),
            (_lexeme.IDENTIFIER, token.Name.Function, "#pop"),
        ],
        # Tokenise include statements (`include` and `defcalgrammar`) that have a special
        # string-literal type not used in the rest of the language.
        "include": [
            (r"[ \r\n\t]+", token.Whitespace),
            (r'"[^"]*"', token.String, "#pop"),
            (r"'[^']*'", token.String, "#pop"),
        ],
        "defcalgrammar": [
            (r"[ \r\n\t]+", token.Whitespace),
            (r'"[^"]*"', _defcalgrammar_callback, "#pop"),
            (r"'[^']*'", _defcalgrammar_callback, "#pop"),
        ],
        # Handle multiline comments.
        "comment": [
            (r"[^*/]+", token.Comment.Multiline),
            (r"/\*", token.Comment.Multiline, "#push"),
            (r"\*/", token.Comment.Multiline, "#pop"),
            (r"[*/]", token.Comment.Multiline),
        ],
        # Used to tokenise blocks that are in the calibration language.
        "cal": [
            (r"[^{}]+", token.Other),
            (r"{", token.Other, "#push"),
            (r"}", token.Other, "#pop"),
        ],
        # Used to tokenise the `cal` and `defcal` statements before the calibration block begins.
        # Override the rule for `{` to enter the `cal` context, since the first bare `{` we
        # encounter (in valid OQ 3) must be the start of the calibration block.
        "cal prelude": [
            (r"{", token.Other, "cal"),
            include("root"),
        ],
    }

    def _get_pulse_lexer(self) -> Union[Lexer, None]:
        """Get a Pygments lexer instance based on the current state of the lexing.

        This returns ``None`` if no suitable lexer can be found."""
        if (
            isinstance(self.__defcal_lexer, str)
            and self.__defcal_lexer in self.__pulse_lexer_overrides
        ):
            return self.__pulse_lexer_overrides[self.__defcal_lexer]
        if isinstance(self.__defcal_lexer, Lexer):
            return self.__defcal_lexer
        try:
            return get_lexer_by_name(self.__defcal_lexer, **self.__options)
        except ClassNotFound:
            return None

    def _delegate_calibration(self, matches: Sequence[Tuple[int, token._TokenType, str]]):
        """Delegate lexing of calibration token stream ``matches`` to an inferred lexer.  This
        function is responsible for organising the match block into

        If no suitable pulse-grammar lexer can be found, the whole pulse block will be lexed into
        ``pygments.token.Other``."""
        if not matches:
            return
        brace_blocks = 0
        if matches[0][2] == "{":
            index, _, value = matches[0]
            yield index, token.Punctuation, value
            matches = matches[1:]
            brace_blocks += 1
        for _, _, value in matches:
            if value == "{":
                brace_blocks += 1
            elif value == "}":
                brace_blocks -= 1
        final_token = None
        if brace_blocks == 0 and matches[-1][2] == "}":
            index, _, value = matches[-1]
            final_token = (index, token.Punctuation, value)
            matches = matches[:-1]
        if matches:
            yield from self._delegate_calibration_inner(
                matches[0][0], "".join(text for _, _, text in matches)
            )
        if final_token is not None:
            yield final_token

    def _delegate_calibration_inner(self, start_index: int, text: str):
        if self.__defcal_lexer is None:
            yield start_index, token.Other, text
            return
        lexer = self._get_pulse_lexer()
        if lexer is None:
            warnings.warn(
                f"No known lexer for alias '{self.__defcal_lexer}'. Not lexing pulse block.",
                category=LexerWarning,
                stacklevel=2,
            )
            yield start_index, token.Other, text
            return
        for index, tokentype, value in lexer.get_tokens_unprocessed(text):
            yield index + start_index, tokentype, value

    def get_tokens_unprocessed(self, text, stack=("root",)):
        # This is similar in principle to pygments.DelegatingLexer, except _we_ are the delegating
        # lexer (rather than some larger manager), and we want to delegate to different lexers
        # dependent on the current value of `defcalgrammar`.
        self.__defcal_lexer = self.__default_defcal_lexer
        calibration_matches = []
        for index, tokentype, value in super().get_tokens_unprocessed(text):
            if tokentype is token.Other:
                calibration_matches.append((index, tokentype, value))
                continue
            if calibration_matches:
                # Drop the surrounding braces from the parts to be tokenised.
                yield from self._delegate_calibration(calibration_matches)
                calibration_matches = []
            yield index, tokentype, value
        # Handle the case of the last token in the block still being in the calibration grammar.
        # This generally shouldn't happen because we should see a final newline token to trigger the
        # grammar tokenisation, but in case that's missing (or the code example doesn't end its
        # ``cal`` block), this flushes the buffer.
        if calibration_matches:
            yield from self._delegate_calibration(calibration_matches)
