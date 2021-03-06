from autodiff import Node
from autodiff import (sin_op, cos_op, tan_op, csc_op, sec_op, cot_op, neg_op, placeholder_op, const_op)
from typing import List, Dict
from enum import Enum
from decimal import Decimal
from Exception.explosion import Explosion
import re


class TokenType(Enum):
    # Value Type #
    NUL = 'null'
    END = 'end, no more token could be parsed'
    VAL = 'value'
    POS = 'unary positive'
    NEG = 'unary negative'
    VAR = 'variable'

    # Operator Type #
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    RMD = '%'
    EXP = '^'
    FACT = '!'

    # Special Symbol #
    PAREN_L = '('
    PAREN_R = ')'
    COMMA = ','

    # Functions ###
    SQRT = 'sqrt'
    POW = 'pow'
    SIN = 'sin'
    COS = 'cos'
    TAN = 'tan'
    SEC = 'sec'
    CSC = 'csc'
    COT = 'cot'


class Token(object):
    def __init__(self, token_type: TokenType) -> None:
        self.type = token_type


class Associative(Enum):
    # Associative #
    LEFT = 'left associative'
    RIGHT = 'right associative'


class RPN(object):

    precedences = {
        TokenType.ADD: 2,
        TokenType.SUB: 2,
        TokenType.MUL: 3,
        TokenType.DIV: 3,
        TokenType.RMD: 3,

        TokenType.SIN: 5,
        TokenType.COS: 5,
        TokenType.TAN: 5,
        TokenType.SEC: 5,
        TokenType.CSC: 5,
        TokenType.COT: 5,

        TokenType.EXP: 4,
        TokenType.SQRT: 10,
        TokenType.POW: 10,
        TokenType.FACT: 20,
        TokenType.NEG: 100,
        TokenType.PAREN_L: 0
    }

    associatives = {
        TokenType.ADD: Associative.LEFT,
        TokenType.SUB: Associative.LEFT,
        TokenType.MUL: Associative.LEFT,
        TokenType.DIV: Associative.LEFT,
        TokenType.RMD: Associative.LEFT,
        TokenType.FACT: Associative.LEFT,
        TokenType.PAREN_R: Associative.LEFT,
        TokenType.EXP: Associative.RIGHT,
        TokenType.SQRT: Associative.RIGHT,
        TokenType.POW: Associative.RIGHT,
        TokenType.SIN: Associative.RIGHT,
        TokenType.COS: Associative.RIGHT,
        TokenType.TAN: Associative.RIGHT,
        TokenType.SEC: Associative.RIGHT,
        TokenType.CSC: Associative.RIGHT,
        TokenType.COT: Associative.RIGHT,
        TokenType.NEG: Associative.RIGHT
    }

    # These operator allows the next operator to be unary operator
    operators_allow_unary_next = [
        TokenType.ADD,
        TokenType.SUB,
        TokenType.MUL,
        TokenType.DIV,
        TokenType.RMD,
        TokenType.EXP,
        TokenType.COMMA,
        TokenType.PAREN_L,
        TokenType.NUL,
        TokenType.NEG
    ]

    operator_pattern = re.compile("^([+-/%*^!(,)])")
    value_pattern = re.compile("^\d+[.]?\d*")
    unary_pattern = re.compile("^([+-]+)")
    naming_pattern = re.compile("^([a-zA-Z]+[a-zA-Z0-9]*)")
    # Used for variable, function naming pattern

    def __init__(self, equation: 'Equation') -> None:
        self.equation = equation
        self.needle = 0  # Used to track the index in string
        self.last_token = Token(TokenType.NUL)
        self.output = []
        self.stack = []
        self.build()

    @classmethod
    def associative(cls, token: 'Token') -> int:
        return RPN.associatives.get(token.type)

    @classmethod
    def precedence(cls, token: 'Token') -> int:
        return RPN.precedences.get(token.type)

    @classmethod
    def get_token_type_by_string(cls, value: str) -> 'Token':
        try:
            return TokenType(value)
        except ValueError:
            return TokenType.NUL

    # Check if the current operator can be unary by looking at previous token
    def can_this_token_be_unary(self) -> bool:
        return self.last_token.type in RPN.operators_allow_unary_next

    def next_token(self) -> Token:
        while (self.needle < len(self.equation.str_eqn) and
                str.isspace(self.equation.str_eqn[self.needle])):
            self.needle += 1

        match = RPN.value_pattern.match(self.equation.str_eqn[self.needle:])
        if (match):
            self.needle += len(match.group())

            ret = Token(TokenType.VAL)
            ret.number = match.group()

            return ret

        match = RPN.unary_pattern.match(self.equation.str_eqn[self.needle:])
        if (match and self.can_this_token_be_unary()):
            self.needle += len(match.group())

            count_neg = 0
            for c in match.group():
                if(c == '-'):
                    count_neg += 1

            if(count_neg % 2 == 0):
                return Token(TokenType.POS)
            else:
                return Token(TokenType.NEG)

        match = RPN.operator_pattern.match(self.equation.str_eqn[self.needle:])
        if (match):
            self.needle += len(match.group())
            return Token(RPN.get_token_type_by_string(match.group()))

        match = RPN.naming_pattern.match(self.equation.str_eqn[self.needle:])
        if (match):
            self.needle += len(match.group())
            name = match.group()
            token_type = RPN.get_token_type_by_string(name)

            # Not a function, treat it as a variable
            if (token_type == TokenType.NUL):
                token = Token(TokenType.VAR)
                token.varname = name
                return token

            else:
                # Return matched function
                return Token(token_type)

        return TokenType.END

    def pop_stack_into_output(self):

        self.output.append(self.stack[-1])
        self.stack.pop()

    def push_stack(self, token: Token):
        if token.type in {TokenType.VAL, TokenType.VAR}:
            if (self.last_token.type == TokenType.PAREN_R or
                    token.type == TokenType.VAR and self.last_token.type == TokenType.VAL):
                self.push_stack(Token(TokenType.MUL))
            self.output.append(token)

        elif token.type in {TokenType.PAREN_R, TokenType.COMMA}:
            while (len(self.stack) > 0 and self.stack[-1].type != TokenType.PAREN_L):
                self.pop_stack_into_output()
            if(len(self.stack) > 0 and self.stack[-1].type == TokenType.PAREN_L):
                self.stack.pop()

        elif token.type in {TokenType.ADD, TokenType.SUB, TokenType.MUL, TokenType.DIV, TokenType.EXP, TokenType.NEG}:
            assoc = RPN.associative(token)
            prece = RPN.precedence(token)
            while(len(self.stack) > 0):

                prece_prev = RPN.precedence(self.stack[-1])
                if (assoc == Associative.LEFT and prece_prev >= prece or
                        assoc == Associative.RIGHT and prece_prev > prece):
                    self.pop_stack_into_output()
                else:
                    break
            self.stack.append(token)

        elif token.type in {TokenType.PAREN_L, TokenType.SIN, TokenType.COS, TokenType.TAN,
                            TokenType.CSC, TokenType.SEC, TokenType.COT}:
            if self.last_token.type in {TokenType.PAREN_R, TokenType.VAL, TokenType.VAR}:
                self.push_stack(Token(TokenType.MUL))
            self.stack.append(token)

    # Build RPN by str_eqn
    def build(self):
        self.needle = 0
        self.stack = []
        self.output = []
        self.last_token = Token(TokenType.NUL)

        while (True):
            token = self.next_token()
            if (token == TokenType.END):
                break
            self.push_stack(token)
            self.last_token = token

        while (len(self.stack) != 0):
            self.pop_stack_into_output()

        return self.output


class Equation(object):
    def __init__(self, equation: str) -> None:
        self.str_eqn = equation
        self.variable_bank = dict()
        self.root = None
        self.build_tree(RPN(self).build())
        self.topo = self.topo_sort(self.root)

    def __repr__(self) -> None:
        return self.root.normal_form

    def __str__(self) -> None:
        return self.root.normal_form

    def topo_sort(self, root: Node) -> [Node]:
        visited = set()
        topo = []

        self.topo_sort_helper(root, topo, visited)

        return topo

    def topo_sort_helper(self, current_node: Node, topo: [], visited: []) -> None:
            if current_node in visited:
                return

            if current_node.inputs is not None:
                for node in current_node.inputs:
                    self.topo_sort_helper(node, topo, visited)

            visited.add(current_node)
            topo.append(current_node)

    list_op_func = {
        TokenType.SIN: sin_op,
        TokenType.COS: cos_op,
        TokenType.TAN: tan_op,
        TokenType.CSC: csc_op,
        TokenType.SEC: sec_op,
        TokenType.COT: cot_op,
        TokenType.NEG: neg_op
    }

    list_const_op_func = {
        TokenType.SIN: lambda x: Decimal(math.sin(x)),
        TokenType.COS: lambda x: Decimal(math.cos(x)),
        TokenType.TAN: lambda x: Decimal(math.tan(x)),
        TokenType.CSC: lambda x: Decimal(1 / math.sin(x)),
        TokenType.SEC: lambda x: Decimal(1 / math.cos(x)),
        TokenType.COT: lambda x: Decimal(1 / math.tan(x)),
        TokenType.NEG: lambda x: Decimal(-x)
    }

    def build_tree(self, rpn: List[Node]) -> Node:
        self.topo = []
        node_queue = []
        for token in rpn:
            if token.type == TokenType.VAL:
                node = const_op(Decimal(token.number))

            elif token.type == TokenType.VAR:
                node = self.get_variable(token.varname)

                # If variable not exists, create the variable and push to bank
                if node is None:
                    node = self.make_variable(token.varname)

            elif token.type in {TokenType.ADD, TokenType.SUB, TokenType.MUL,
                                TokenType.DIV, TokenType.EXP, TokenType.RMD, TokenType.POW}:
                if (len(node_queue) < 2):
                    Explosion.EQUATION_BUILD_TREE_MISMATCHED_OPERAND.bang()

                first = node_queue[-2]
                second = node_queue[-1]
                node_queue.pop(), node_queue.pop()

                if token.type == TokenType.ADD:
                    node = first + second
                elif token.type == TokenType.SUB:
                    node = first - second
                elif token.type == TokenType.MUL:
                    node = first * second
                elif token.type == TokenType.DIV:
                    node = first / second
                elif token.type == TokenType.EXP:
                    node = first ** second
                else:
                    raise ValueError("Unsupported yet")

            elif token.type in {TokenType.NEG, TokenType.SIN, TokenType.COS, TokenType.TAN,
                                TokenType.CSC, TokenType.SEC, TokenType.COT}:
                if (len(node_queue) < 1):
                    raise ValueError("SyntaxError: mismatched operand.")

                first = node_queue[-1]
                node_queue.pop()

                is_const = True if (first.op == const_op) else False

                if is_const:
                    node = const_op(Equation.list_const_op_func[token.type](first.const_attr))
                else:
                    node = Equation.list_op_func[token.type](first)

            elif token.type == TokenType.PAREN_L:
                continue

            node_queue.append(node)

        if(len(node_queue) != 1):
            raise ValueError("SyntaxError: something went wrong.")

        self.root = node_queue[0]

    def get_variable(self, var_name: str) -> Node:
        if (var_name in self.variable_bank):
            return self.variable_bank[var_name]
        else:
            return None

    def make_variable(self, var_name: str) -> Node:
        variable = self.variable_bank[var_name] = placeholder_op(var_name)
        return variable

    # Ex: z = x+y
    # dz/dx = [1,0]
    # dz/dy = [0,1]
    def eval_diff_form(self, diff_parts: {str}) -> 'Equation':
        eqn = self
        for part in diff_parts:
            for node in eqn.topo:
                node.op.diff(node, part)
            # print(eqn.root.normal_form + ' | ', end='')
            # print(eqn.root.diff_form)
            eqn = Equation(eqn.root.diff_form)

        return eqn

    def eval_normal_form(self, variable_parts: Dict[str, float]) -> Decimal:
        value_nodes = dict()
        for node in self.topo:
            if node.op is placeholder_op:
                if node.normal_form in variable_parts:
                    value_nodes[node] = Decimal(variable_parts[node.normal_form])
                else:
                    value_nodes[node] = 0
            elif node.op is const_op:
                value_nodes[node] = node.const_attr
            else:
                input_vals = []
                for input in node.inputs:
                    input_vals.append(value_nodes[input])
                value_nodes[node] = node.op.compute(node, input_vals)

        return value_nodes[self.root]

    def get_normal_form(self) -> str:
        pass


if __name__ == '__main__':
    b = Equation('(tan (y^2))')
    print(b)
    diff_x_y = b.eval_diff_form(['y'])
    print(diff_x_y)
    print(diff_x_y.eval_normal_form({'x': 1290}))

    b = Equation('7 + x^2 - 3*x*y + 3.25*y^2 - 4*y')
    print(b)
    print(b.eval_diff_form(['x']))
    print(b.eval_normal_form({'x': 50, 'y': 30}))

    b = Equation('x*y/sin(cos x * y)sin(x)sin y + sin z sin a')
    print(b)
    print(b.eval_normal_form({'x': 10, 'y': 90, 'z': 0}))

    # print(b.root.normal_form)
    '''
    b = Equation('(3)')
    a = RPN(b).output
    for token in a:
        if (token.type == TokenType.END): break
        print(token.type.name, end = ' ')
        if (token.type == TokenType.VAL):
            print(token.number)
        elif (token.type == TokenType.VAR):
            print(token.varname)
        else:
            print(token.type.value)
    '''
