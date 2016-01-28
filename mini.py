from parsimonious.grammar import Grammar
import ast


class Mini(object):
    def __init__(self, env={}):
        self.env = env
        # Add built-in functions
        self.env['sum'] = lambda *args: sum(args)
        self.text = ''

    def __line(self, node):
        """Return the 1-based line number"""
        return self.text.count('\n', 0, node.start) + 1

    def __column(self, node):
        """Return the 1-based column"""
        try:
            return node.start - self.text.rindex('\n', 0, node.start)
        except ValueError:
            return node.start + 1

    def parse(self, source, grammar_rule="program"):
        # Extract grammar rules from doc strings
        grammar = '\n'.join(v.__doc__ for k, v in vars(self.__class__).items()
                            if '__' not in k and hasattr(v, '__doc__') and v.__doc__)
        return Grammar(grammar)[grammar_rule].parse(source)

    def _eval(self, node):
        method = getattr(self, node.expr_name, lambda node, children: children)
        return method(node, [self._eval(n) for n in node])

    def compile(self, source):
        # Compile an expression
        parsed = self.get_ast(source, 'program')
        fixed = ast.fix_missing_locations(parsed)
        codeobj = compile(fixed, '<string>', 'exec')
        eval(codeobj, self.env)

    def eval(self, source):
        # Evaluate an expression
        parsed = self.get_ast(source, 'expressions')
        fixed = ast.fix_missing_locations(parsed)
        codeobj = compile(fixed, '<string>', 'eval')
        return eval(codeobj, self.env)

    def get_ast(self, source, grammar_rule):
        self.text = source
        node = self.parse(source, grammar_rule)
        return self._eval(node)

    # --------------------------------------------------------------------------------------------------------
    # Grammar methods
    #

    def program(self, node, children):
        'program = statement+'
        return ast.Module(body=children,
                          lineno=self.__line(node),
                          col_offset=self.__column(node)
                          )

    def statement(self, node, children):
        'statement = _ (func / assignment) _'
        return children[1][0]

    def expressions(self, node, children):
        'expressions = expr*'
        exp = ast.Expression(
                ast.List(
                        elts=children,
                        ctx=ast.Load(),
                        lineno=self.__line(node),
                        col_offset=self.__column(node)
                )
        )
        return exp

    def func(self, node, children):
        'func = name _ "=" _ "(" parameters ")" _ "->" _ expr'
        name, _, _equals, _, lbrace, params, rbrace, _, _arrow, _, expr = children

        # Name will return us an AST node called name, we just need it's name
        name = name.id

        funcdef = ast.FunctionDef(name=name,
                                  args=ast.arguments(
                                          args=params,
                                          vararg=None, kwarg=None, defaults=[],
                                          lineno=self.__line(node),
                                          col_offset=self.__column(node)

                                  ),
                                  body=[ast.Return(value=expr,
                                                   lineno=expr.lineno,
                                                   col_offset=expr.col_offset
                                                   )],
                                  decorator_list=[],
                                  lineno=self.__line(node),
                                  col_offset=self.__column(node)
                                  )
        return funcdef

    def parameters(self, node, children):
        'parameters = parameter*'
        return children

    def parameter(self, node, children):
        'parameter = ~"[a-z]+" _ '
        return ast.Name(id=node.text.strip(),
                        ctx=ast.Param(),
                        lineno=self.__line(node),
                        col_offset=self.__column(node)
                        )

    def expr(self, node, children):
        'expr = _ (ifelse / call / infix / number / name) _'
        return children[1][0]

    def ifelse(self, node, children):
        'ifelse = "if" _ expr _ "then" _ expr _ "else" _ expr'
        _if, _, cond, _, _then, _, cons, _, _else, _, alt = children
        return ast.IfExp(test=cond, body=cons, orelse=alt,
                         lineno=self.__line(node),
                         col_offset=self.__column(node)
                         )

    def call(self, node, children):
        'call = name "(" arguments ")"'
        name, lbrace, args, rbrace = children

        return ast.Call(
                func=name,
                args=args,
                keywords=[],
                lineno=self.__line(node),
                col_offset=self.__column(node)
        )

    def arguments(self, node, children):
        'arguments = argument*'
        return children

    def argument(self, node, children):
        'argument = expr _'
        return children[0]

    def infix(self, node, children):
        'infix = "(" _ expr _ operator _ expr _ ")"'
        _lbrace, _, expr1, _, op, _, expr2, _, rbrace = children
        return ast.BinOp(
                expr1,
                op,
                expr2,
                lineno=self.__line(node),
                col_offset=self.__column(node)
        )

    def operator(self, node, children):
        'operator = "+" / "-" / "*" / "/"'
        operators = {"+": ast.Add, "-": ast.Sub, "*": ast.Mult, "/": ast.Div}
        return operators[node.text.strip()](lineno=self.__line(node), col_offset=self.__column(node))

    def number(self, node, children):
        'number = ~"[0-9]+"'
        return ast.Num(int(node.text),
                       lineno=self.__line(node),
                       col_offset=self.__column(node)
                       )

    def name(self, node, children):
        'name = ~"[a-z]+" _ '
        return ast.Name(id=node.text.strip(),
                        ctx=ast.Load(),
                        lineno=self.__line(node),
                        col_offset=self.__column(node)
                        )

    def assignment(self, node, children):
        'assignment = lvalue _ "=" _ expr'
        lvalue, _, equals, _, expr = children
        return ast.Assign(targets=[lvalue],
                          value=expr,
                          lineno=self.__line(node),
                          col_offset=self.__column(node)
                          )

    def lvalue(self, node, children):
        'lvalue = ~"[a-z]+" _ '
        return ast.Name(id=node.text.strip(),
                        ctx=ast.Store(),
                        lineno=self.__line(node),
                        col_offset=self.__column(node)
                        )

    def _(self, node, children):
        '_ = ~"\s*"'
