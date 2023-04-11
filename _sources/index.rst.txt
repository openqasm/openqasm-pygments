Pygments Tools for OpenQASM
===========================

.. module:: openqasm_pygments

This project contains Pygments lexers for OpenQASM 2, OpenQASM 3, and the
pulse-calibration dialect OpenPulse.  These will all register themselves with
Pygments by suitable aliases (``qasm2``, ``qasm3`` and ``openpulse``, among
others).

OpenQASM Lexers
---------------

This package contains lexers for both OpenQASM 2 and 3.

.. autoclass:: OpenQASM3Lexer
   :class-doc-from: class

.. autoclass:: OpenQASM2Lexer
   :class-doc-from: class


Pulse Grammar Lexers for OpenQASM 3
-----------------------------------

There is currently a single lexer for pulse calibration.

.. autoclass:: OpenPulseLexer
   :class-doc-from: class
