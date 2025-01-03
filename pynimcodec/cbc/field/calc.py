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


allowed_functions = {
    'round': round,
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
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in allowed_functions:
            func = allowed_functions[node.func.id]
            args = [eval_(arg) for arg in node.args]
            return func(*args)
        raise ValueError(f'Unsafe function: {node.func.id}')
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
