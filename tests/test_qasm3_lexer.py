import pytest
from pygments import token
from pygments.lexer import RegexLexer
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from openqasm_pygments import OpenQASM3Lexer, LexerWarning


def _remove_whitespace(tokens):
    return [(token_, text) for (token_, text) in tokens if token_ is not token.Text.Whitespace]


class DummyLexer(RegexLexer):
    name = "Dummy Regex"
    aliases = ["testing-dummy"]
    filenames = []
    tokens = {"root": [("^.+$", token.Text)]}


def test_function_lookahead(lexer_qasm3):
    text = """
gate f q {}
def f() {}
f a;
f(1);
f(1) a;
"""
    assert _remove_whitespace(lexer_qasm3.get_tokens(text)) == [
        (token.Keyword.Declaration, "gate"),
        (token.Name.Function, "f"),
        (token.Name, "q"),
        (token.Punctuation, "{"),
        (token.Punctuation, "}"),
        (token.Keyword.Declaration, "def"),
        (token.Name.Function, "f"),
        (token.Punctuation, "("),
        (token.Punctuation, ")"),
        (token.Punctuation, "{"),
        (token.Punctuation, "}"),
        (token.Name.Function, "f"),
        (token.Name, "a"),
        (token.Punctuation, ";"),
        (token.Name.Function, "f"),
        (token.Punctuation, "("),
        (token.Number, "1"),
        (token.Punctuation, ")"),
        (token.Punctuation, ";"),
        (token.Name.Function, "f"),
        (token.Punctuation, "("),
        (token.Number, "1"),
        (token.Punctuation, ")"),
        (token.Name, "a"),
        (token.Punctuation, ";"),
    ]


def test_for_loop_variable_not_callable(lexer_qasm3):
    text = "for uint i in a {}"
    assert _remove_whitespace(lexer_qasm3.get_tokens(text)) == [
        (token.Keyword, "for"),
        (token.Keyword.Type, "uint"),
        (token.Name, "i"),
        (token.Keyword, "in"),
        (token.Name, "a"),
        (token.Punctuation, "{"),
        (token.Punctuation, "}"),
    ]


class TestPulseLexerDelegation:
    def test_inferred_known_alias(self, lexer_qasm3):
        # This uses a very (!) non-standard pulse-grammar lexer to test delegation
        # to Pygments aliases is working correctly.
        text = 'defcalgrammar "python3";\ncal {pass}\n'
        assert _remove_whitespace(lexer_qasm3.get_tokens(text)) == [
            (token.Keyword.Namespace, "defcalgrammar"),
            (token.Literal.String, '"python3"'),
            (token.Punctuation, ";"),
            (token.Keyword, "cal"),
            (token.Punctuation, "{"),
            (token.Keyword, "pass"),
            (token.Punctuation, "}"),
        ]

    def test_inferred_to_lexer_instance(self):
        lexer = OpenQASM3Lexer(default_pulse_lexer=DummyLexer(), infer_pulse_grammar=True)
        # The alias here (which Pygments doesn't know about), should cause a warning to be emitted
        # and the calibration grammar to be tokenised to `Other` if the inference actually takes
        # effect.  This tests that the short-circuit logic in the lexer look-up works, i.e. that the
        # `OpenQASM3Lexer` sees that the given default lexer has `testing-dummy` in its aliases, and
        # so uses it directly, rather than asking Pygments.
        with pytest.raises(ClassNotFound):
            # If this doesn't raise an error, somehow the alias has got itself registered.
            get_lexer_by_name("testing-dummy")
        text = "defcalgrammar 'testing-dummy'; cal {All this is just text.}\n"
        assert _remove_whitespace(lexer.get_tokens(text)) == [
            (token.Keyword.Namespace, "defcalgrammar"),
            (token.Literal.String, "'testing-dummy'"),
            (token.Punctuation, ";"),
            (token.Keyword, "cal"),
            (token.Punctuation, "{"),
            (token.Text, "All this is just text."),
            (token.Punctuation, "}"),
        ]

    def test_inferred_to_override(self):
        lexer = OpenQASM3Lexer(pulse_lexer_overrides={"openpulse": DummyLexer()})
        text = "defcalgrammar 'openpulse'; cal {All this is just text.}\n"
        assert _remove_whitespace(lexer.get_tokens(text)) == [
            (token.Keyword.Namespace, "defcalgrammar"),
            (token.Literal.String, "'openpulse'"),
            (token.Punctuation, ";"),
            (token.Keyword, "cal"),
            (token.Punctuation, "{"),
            (token.Text, "All this is just text."),
            (token.Punctuation, "}"),
        ]

    def test_no_default_no_defcalgrammar(self):
        lexer = OpenQASM3Lexer(default_pulse_lexer=None)
        text = "cal {All this is just other.}\n"
        assert _remove_whitespace(lexer.get_tokens(text)) == [
            (token.Keyword, "cal"),
            (token.Punctuation, "{"),
            # Note this remains 'Other', as opposed to 'Text', which is what the dummy does.
            (token.Other, "All this is just other."),
            (token.Punctuation, "}"),
        ]

    def test_default_no_defcalgrammar(self):
        lexer = OpenQASM3Lexer(default_pulse_lexer=DummyLexer())
        text = "cal {All this is just text.}\n"
        assert _remove_whitespace(lexer.get_tokens(text)) == [
            (token.Keyword, "cal"),
            (token.Punctuation, "{"),
            (token.Text, "All this is just text."),
            (token.Punctuation, "}"),
        ]

    def test_unknown_alias_warns(self, lexer_qasm3):
        text = "defcalgrammar 'unknown-alias';\ncal {All this is just other.}\n"
        with pytest.warns(LexerWarning, match="No known lexer for alias 'unknown-alias'"):
            tokens = list(lexer_qasm3.get_tokens(text))
        assert _remove_whitespace(tokens) == [
            (token.Keyword.Namespace, "defcalgrammar"),
            (token.Literal.String, "'unknown-alias'"),
            (token.Punctuation, ";"),
            (token.Keyword, "cal"),
            (token.Punctuation, "{"),
            (token.Other, "All this is just other."),
            (token.Punctuation, "}"),
        ]

    def test_force_no_inference(self):
        lexer = OpenQASM3Lexer(default_pulse_lexer="openpulse", infer_pulse_grammar=False)
        text = "defcalgrammar 'python3';\ncal {pass}\n"
        assert _remove_whitespace(lexer.get_tokens(text)) == [
            (token.Keyword.Namespace, "defcalgrammar"),
            (token.Literal.String, "'python3'"),
            (token.Punctuation, ";"),
            (token.Keyword, "cal"),
            (token.Punctuation, "{"),
            # Since we default to 'openpulse' and forbid inference, this should be lexed as a
            # general name, whereas if it is lexed with the Python 3 lexer, it will be a keyword.
            (token.Name, "pass"),
            (token.Punctuation, "}"),
        ]

    def test_no_final_newline(self, lexer_qasm3):
        text = 'defcalgrammar "openpulse";\ncal {extern port port0;}'
        assert _remove_whitespace(lexer_qasm3.get_tokens(text)) == [
            (token.Keyword.Namespace, "defcalgrammar"),
            (token.Literal.String, '"openpulse"'),
            (token.Punctuation, ";"),
            (token.Keyword, "cal"),
            (token.Punctuation, "{"),
            (token.Keyword.Type, "extern"),
            (token.Keyword.Type, "port"),
            (token.Name, "port0"),
            (token.Punctuation, ";"),
            (token.Punctuation, "}"),
        ]

    def test_unclosed_block(self, lexer_qasm3):
        text = 'defcalgrammar "openpulse";\ncal {extern port port0;'
        assert _remove_whitespace(lexer_qasm3.get_tokens(text)) == [
            (token.Keyword.Namespace, "defcalgrammar"),
            (token.Literal.String, '"openpulse"'),
            (token.Punctuation, ";"),
            (token.Keyword, "cal"),
            (token.Punctuation, "{"),
            (token.Keyword.Type, "extern"),
            (token.Keyword.Type, "port"),
            (token.Name, "port0"),
            (token.Punctuation, ";"),
        ]
