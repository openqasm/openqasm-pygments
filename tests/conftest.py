import os
import pathlib
from typing import Union, List

import pytest

import openqasm_pygments

TEST_DIR = pathlib.Path(__file__).parent
REPO_DIR = TEST_DIR.parent


@pytest.fixture
def lexer_qasm3():
    yield openqasm_pygments.OpenQASM3Lexer()


@pytest.fixture
def lexer_qasm2():
    yield openqasm_pygments.OpenQASM2Lexer()


@pytest.fixture
def lexer_openpulse():
    yield openqasm_pygments.OpenPulseLexer()


def find_files(directory: Union[str, os.PathLike], suffix: str = "", raw: bool = False) -> List:
    """Recursively find all files in ``directory`` that end in ``suffix``.

    Args:
        directory: the (absolute) directory to search for the files.
        suffix: the string that filenames should end in to be returned.  Files
            without this suffix are ignored.  This is useful for limiting files
            to those with a particular extension.
        raw: If false (the default), the output elements are all
        ``pytest.param`` instances with nice ids.  If true, then only the file
        names are returned, without the wrapping parameter.

    Returns:
        By default, a list of ``pytest`` parameters, where the value is a string
        of the absolute path to a file, and the id is a string of the path
        relative to the given directory.  If ``raw`` is given, then just a list
        of the files as ``pathlib.Path`` instances.
    """
    directory = pathlib.Path(directory).absolute()

    if raw:

        def output_format(root, file):
            return str(pathlib.Path(root) / file)

    else:

        def output_format(root, file):
            path = pathlib.Path(root) / file
            return pytest.param(str(path), id=str(path.relative_to(directory)))

    return [
        output_format(root, file)
        for root, _, files in os.walk(directory)
        for file in files
        if file.endswith(suffix)
    ]
