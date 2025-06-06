# Rewrite the output files in the `tests/examples` with the new output of the lexer.  The resulting
# output should be checked that it is actually correct, since this blesses things for the new test
# suite.

import pathlib
import openqasm_pygments


def rewrite(fname, lexer):
    with open(fname, "r", encoding="utf-8") as fptr:
        content = fptr.read().strip()
    return "\n".join(
        f"{repr(token):<19s} {ttype}" for ttype, token in lexer.get_tokens(content)
    )


if __name__ == "__main__":
    repo_root = pathlib.Path(__file__).parents[1]
    examples_dir = repo_root / "tests" / "examples"
    configs = [
        (examples_dir / "qasm2", (".qasm", ".inc"), openqasm_pygments.OpenQASM2Lexer()),
        (examples_dir / "qasm3", (".qasm",), openqasm_pygments.OpenQASM3Lexer()),
        (
            examples_dir / "openqasm",
            (".openpulse",),
            openqasm_pygments.OpenPulseLexer(),
        ),
    ]
    for dir_, suffixes, lexer in configs:
        for suffix in suffixes:
            for file in dir_.glob(f"**/*{suffix}"):
                new_tokens = rewrite(file, lexer)
                with open(str(file) + ".output", "w", encoding="utf-8") as fptr:
                    print(new_tokens, file=fptr)
