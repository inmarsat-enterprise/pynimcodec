"""Calculation utilities for field value manipulation."""

import ast
import operator as op


operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    # ast.BitXor: op.xor,
    ast.USub: op.neg,
    ast.Invert: op.neg,
}


def eval_(node):
    """Recursively evaluates the nodes of a mathematical expression."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
    elif isinstance(node, ast.BinOp):
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp):
        return operators[type(node.op)](eval_(node.operand))
    raise TypeError(node)


def is_valid_expr(expr: str) -> bool:
    """Check if an expression is valid."""
    if not isinstance(expr, str) or 'v' not in expr:
        return False
    try:
        eval_(ast.parse(expr.replace('v', '1'), mode='eval').body)
        return True
    except TypeError:
        return False


def calc_decode(decalc: str, encoded: int):
    """"""
    if not isinstance(encoded, int):
        raise ValueError('Invalid encoded integer')
    if decalc == '':
        return encoded
    if not isinstance(decalc, str) or 'v' not in decalc:
        raise ValueError('Invalid decalc statement')
    expr = decalc.replace('v', f'{encoded}')
    return eval_(ast.parse(expr, mode='eval').body)


def calc_encode(encalc: str, decoded: 'int|float'):
    """"""
    if not isinstance(decoded, (int, float)):
        raise ValueError('Invalid decoded number')
    if encalc == '':
        return decoded
    if not isinstance(encalc, str) or 'v' not in encalc:
        raise ValueError('Invalid decalc statement')
    expr = encalc.replace('v', f'{decoded}')
    return int(eval_(ast.parse(expr, mode='eval').body))


if __name__ == '__main__':
    print(calc_decode('v+1', 1))
    print(calc_decode('v**3', 2))
    print(calc_decode('2**v-1', 8))
    print(calc_encode('v*10', 42.2))
    print(calc_encode('v*10', -42.2))
    print(calc_encode('v*10', 42.26))
    print(calc_decode('v/10', 422))
    print(calc_decode('-v', 1))
    print(calc_decode('~v', -1))
