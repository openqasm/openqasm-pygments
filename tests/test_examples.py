import ast

import pytest
from pygments.token import string_to_tokentype

from .conftest import find_files, TEST_DIR


def _split_example_output_file(file):
    for line in file:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        prefix, token_type = line.rsplit(maxsplit=1)
        token_text = ast.literal_eval(prefix.strip())
        yield string_to_tokentype(token_type), token_text


@pytest.mark.parametrize(
    "filename",
    find_files(TEST_DIR / "examples" / "qasm2", suffix=".qasm")
    + find_files(TEST_DIR / "examples" / "qasm2", suffix=".inc"),
)
def test_qasm2_examples(filename, lexer_qasm2):
    with open(filename, "r", encoding="utf-8") as file:
        qasm = file.read().strip()
    with open(filename + ".output", "r", encoding="utf-8") as file:
        token_stream = list(_split_example_output_file(file))
    assert list(lexer_qasm2.get_tokens(qasm)) == token_stream


@pytest.mark.parametrize("filename", find_files(TEST_DIR / "examples" / "qasm3", suffix=".qasm"))
def test_qasm3_examples(filename, lexer_qasm3):
    with open(filename, "r", encoding="utf-8") as file:
        qasm = file.read().strip()
    with open(filename + ".output", "r", encoding="utf-8") as file:
        token_stream = list(_split_example_output_file(file))
    assert list(lexer_qasm3.get_tokens(qasm)) == token_stream


@pytest.mark.parametrize(
    "filename", find_files(TEST_DIR / "examples" / "openpulse", suffix=".openpulse")
)
def test_openpulse_examples(filename, lexer_openpulse):
    with open(filename, "r", encoding="utf-8") as file:
        qasm = file.read().strip()
    with open(filename + ".output", "r", encoding="utf-8") as file:
        token_stream = list(_split_example_output_file(file))
    assert list(lexer_openpulse.get_tokens(qasm)) == token_stream
