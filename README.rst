Mini: Compiler and a programming language implemented in Python
===============================================================

Inspired by the screencast by Vladimir Keleshev :

`How to write an interpreter in Python <http://youtu.be/1h1mM7VwNGo>`_.

and the source for his Mini interpreter in github :

https://github.com/keleshev/mini

This version implements the same language but uses the Python AST module to generate an AST and
compile it into a Python code object. This can then be used to evaluate expressions.

Since Python makes the distinction between statements and expressions I provide a compile(source) method
and an eval(source) method. See the tests (which I converted to Unittest).

It uses:

* `The Python AST module <http://docs.python.org/2.7/library/ast>`_
   for generating a python Abstract Syntax Tree

* `parsimonious <https://github.com/erikrose/parsimonious>`_
  library for parsing using Parsing Expression Grammar (PEG)
  (See also the original `PEG paper
  <http://pdos.csail.mit.edu/papers/parsing:popl04.pdf>`_).
