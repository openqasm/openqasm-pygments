project = 'OpenQASM Pygments Tools'
copyright = '2022, OpenQASM contributors'
author = 'OpenQASM contributors'
version = "0.1.1"

extensions = [
    "sphinx.ext.autodoc",
]
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Document the docstring for the class and the __init__ method together.
autoclass_content = "both"

html_theme = 'alabaster'
