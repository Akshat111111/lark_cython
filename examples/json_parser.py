"""
Simple JSON Parser
==================

The code is short and clear, and outperforms every other parser (that's written in Python).

Adapted from the Lark JSON example (lark/examples/json_parser.py).

Main differences from Lark's example code:

- We use the _plugins option to override Lark's internal lexer+parser implementation

- Since Tokens don't inherit from str, we have to explicitly use "token.value".

"""
import sys

from lark import Lark, Transformer, v_args
import lark_cython

json_grammar = r"""
    ?start: value

    ?value: object
          | array
          | string
          | SIGNED_NUMBER      -> number
          | "true"             -> true
          | "false"            -> false
          | "null"             -> null

    array  : "[" [value ("," value)*] "]"
    object : "{" [pair ("," pair)*] "}"
    pair   : string ":" value

    string : ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS

    %ignore WS
"""


class TreeToJson(Transformer):
    @v_args(inline=True)
    def string(self, s):
        return s.value[1:-1].replace('\\"', '"')

    @v_args(inline=True)
    def number(self, n):
        return float(n.value)

    array = list
    pair = tuple
    object = dict

    null = lambda self, _: None
    true = lambda self, _: True
    false = lambda self, _: False


### Create the JSON parser with Lark-Cython, using the LALR algorithm
json_parser = Lark(json_grammar, parser='lalr',
                   # Use Cython for the lexer+parser
                   _plugins=lark_cython.plugins,

                   # Using the basic lexer isn't required, and isn't usually recommended.
                   # But, it's good enough for JSON, and it's slightly faster.
                   lexer='basic',
                   # Disabling propagate_positions and placeholders slightly improves speed
                   propagate_positions=False,
                   maybe_placeholders=False,
                   # Using an internal transformer is faster and more memory efficient
                   transformer=TreeToJson())
parse = json_parser.parse


def test():
    test_json = '''
        {
            "empty_object" : {},
            "empty_array"  : [],
            "booleans"     : { "YES" : true, "NO" : false },
            "numbers"      : [ 0, 1, -2, 3.3, 4.4e5, 6.6e-7 ],
            "strings"      : [ "This", [ "And" , "That", "And a \\"b" ] ],
            "nothing"      : null
        }
    '''

    j = parse(test_json)
    print(j)
    import json
    assert j == json.loads(test_json)


if __name__ == '__main__':
    # test()
    with open(sys.argv[1]) as f:
        print(parse(f.read()))
