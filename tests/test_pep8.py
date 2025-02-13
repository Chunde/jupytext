import pytest
from testfixtures import compare
from jupytext import readf, reads, writes
from jupytext.pep8 import next_instruction_is_function_or_class, cell_ends_with_function_or_class
from jupytext.pep8 import cell_ends_with_code, cell_has_code, pep8_lines_between_cells
from .utils import list_notebooks


def test_next_instruction_is_function_or_class():
    text = """@pytest.mark.parametrize('py_file',
    [py_file for py_file in list_notebooks('../jupytext') + list_notebooks('.') if
                                     py_file.endswith('.py')])
def test_no_metadata_when_py_is_pep8(py_file):
    pass
"""
    assert next_instruction_is_function_or_class(text.splitlines())


def test_cell_ends_with_code():
    assert not cell_ends_with_code([])


def test_cell_ends_with_function_or_class():
    text = """class A:
    __init__():
    '''A docstring
with two lines or more'''
        self.a = 0
"""
    assert cell_ends_with_function_or_class(text.splitlines())

    lines = ['#', '#']
    assert not cell_ends_with_function_or_class(lines)

    text = """# two blank line after this class
class A:
    pass


# so we do not need to insert two blank lines below this cell
    """
    assert not cell_ends_with_function_or_class(text.splitlines())

    text = """# All lines
# are commented"""
    assert not cell_ends_with_function_or_class(text.splitlines())

    text = """# Two blank lines after function
def f(x):
    return x


# And a comment here"""
    assert not cell_ends_with_function_or_class(text.splitlines())

    assert not cell_ends_with_function_or_class(['', '#'])


def test_pep8_lines_between_cells():
    prev_lines = """a = a_long_instruction(
    over_two_lines=True)""".splitlines()

    next_lines = """def f(x):
    return x""".splitlines()

    assert cell_ends_with_code(prev_lines)
    assert next_instruction_is_function_or_class(next_lines)
    assert pep8_lines_between_cells(prev_lines, next_lines, '.py') == 2


def test_pep8_lines_between_cells_bis():
    prev_lines = """def f(x):
    return x""".splitlines()

    next_lines = """# A markdown cell

# An instruction
a = 5
""".splitlines()

    assert cell_ends_with_function_or_class(prev_lines)
    assert cell_has_code(next_lines)
    assert pep8_lines_between_cells(prev_lines, next_lines, '.py') == 2

    next_lines = """# A markdown cell

# Only markdown here
# And here
""".splitlines()

    assert cell_ends_with_function_or_class(prev_lines)
    assert not cell_has_code(next_lines)
    assert pep8_lines_between_cells(prev_lines, next_lines, '.py') == 1


def test_pep8():
    text = """import os

path = os.path


# code cell #1, with a comment on f
def f(x):
    return x + 1


# markdown cell #1

# code cell #2 - an instruction
a = 4


# markdown cell #2

# code cell #3 with a comment on g
def g(x):
    return x + 1


# markdown cell #3

# the two lines are:
# - right below the function/class
# - below the last python paragraph (i.e. NOT ABOVE g)

# code cell #4
x = 4
"""
    nb = reads(text, 'py')
    for cell in nb.cells:
        assert not cell.metadata

    text2 = writes(nb, 'py')
    compare(text, text2)


def test_pep8_bis():
    text = """# This is a markdown cell

# a code cell
def f(x):
    return x + 1

# And another markdown cell
# Separated from f by just one line
# As there is no code here
"""
    nb = reads(text, 'py')
    for cell in nb.cells:
        assert not cell.metadata

    text2 = writes(nb, 'py')
    compare(text, text2)


@pytest.mark.parametrize('py_file', [py_file for py_file in list_notebooks('../jupytext') + list_notebooks('.') if
                                     py_file.endswith('.py')])
def test_no_metadata_when_py_is_pep8(py_file):
    nb = readf(py_file)

    for i, cell in enumerate(nb.cells):
        if i == 0 and not cell.source:
            assert cell.metadata == {'lines_to_next_cell': 0}, py_file
        else:
            assert not cell.metadata, (py_file, cell.source)
