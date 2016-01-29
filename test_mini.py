from mini import Mini
import unittest


class MiniTestCase(unittest.TestCase):
    """Basic tests"""

    def setUp(self):
        self.m = Mini()

    def test_numbers(self):
        self.assertTrue(self.m.eval('') == [])
        self.assertTrue(self.m.eval('42') == [42])
        self.assertTrue(self.m.eval('42 12') == [42, 12])

    def test_operators(self):
        self.assertTrue(self.m.eval('(42 + 2)') == [44])
        self.assertTrue(self.m.eval('(42 + ( 2 * 4))') == [50])

    def test_functions(self):
        self.assertTrue(self.m.eval('sum(10 20)') == [30])
        self.assertTrue(self.m.eval('sum()') == [0])

    def test_if(self):
        self.assertTrue(self.m.eval('if 1 then 42 else 12') == [42])
        self.assertTrue(self.m.eval('if 0 then 42 else 12') == [12])

class MiniCompileTestCase(unittest.TestCase):
    """Compilation test cases"""

    def setUp(self):
        self.m = Mini()

    def test_addten(self):
        self.m.compile('addten = (b) -> (b + 10)')
        self.assertTrue(self.m.eval('addten(2)') == [12])

    def test_addx(self):
        source = 'x = 10 \n addx = (a) -> (a + x)'
        self.m.compile(source)
        self.assertTrue(self.m.env['x'] == 10)
        self.assertTrue(self.m.eval('addx(2)') == [12])

    def test_add(self):
        self.m.compile('add = (a b) -> (a + b)')
        self.assertTrue(self.m.eval('add(42 12)')[-1] == 54)

    def test_factorial(self):
        # 0 => 1
        # => n * (n - 1)!
        source = '''
factorial = (n) ->
if n then
(n * factorial((n - 1)))
else
1
'''
        self.m.compile(source)
        self.assertTrue(self.m.eval('factorial(0)') == [1])
        self.assertTrue(self.m.eval('factorial(5)') == [120])

if __name__ == '__main__':
    unittest.main()
