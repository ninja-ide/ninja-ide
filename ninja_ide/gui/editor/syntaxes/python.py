import builtins

# FIXME: match complex number

kwlist = ['and', 'as', 'assert', 'break', 'await', 'continue', 'del', 'def',
          'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if',
          'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass',
          'raise', 'return', 'try', 'while', 'with', 'yield', 'async']

syntax = {
    'formats': {
        'builtin': '%(syntax_builtin)s',
        'comment': '%(syntax_comment)s',
        'decorator': '%(syntax_decorator)s',
        'keyword': '%(syntax_keyword)s',
        'number': '%(syntax_number)s',
        'hexnumber': '%(syntax_hexnumber)s',
        'binnumber': '%(syntax_binnumber)s',
        'octnumber': '%(syntax_octnumber)s',
        'definition': '%(syntax_definition)s',
        'proper_object': '%(syntax_proper_object)s',
        'string': '%(syntax_string)s',
        'rstring': '%(syntax_rstring)s',
        'docstring': '%(syntax_docstring)s',
        'operators': '%(syntax_operators)s',
        'definitionname': '%(syntax_definitionname)s',
        'function': '%(syntax_function)s',
        'constant': '%(syntax_constant)s'
    },
    'partitions': [
        ('comment', "#", '\n'),
        ("docstring", "[buBU]?'''", "'''", True),
        ("rstring", "[rR]'''", "'''", True),
        ("rstring", '[rR]"""', '"""', True),
        ("string", "[buBU]?'", "'"),
        ("docstring", '[buBU]?"""', '"""', True),
        ("string", '[buBU]?"', '"'),
    ],
    'scanner': {
        # FIXME: Underscores in numeric literals
        None: [
            ('constant', "\\b_*[A-Z][_\d]*[A-Z][A-Z\d]*(_\w*)?\\b"),
            ('function', "\w+(?=\ *?\()"),
            ('hexnumber', '0[xX]\d+'),
            ('octnumber', '0[oO](_?[0-7])+'),
            ('binnumber', '0[bB][01]+'),
            ('number', '(?<!\w)(\.?)(_?\d+)+(\.\d*)?[lL]?'),
            ('decorator', "@\w+(\.\w+)?"),
            ('definition',
             ["(?<=def)\ +?\w+(?=\ *?\()",
              "(?<=class)\ +?\w+(?=\ *?\()"]),
            ('definitionname', 'class|def', '(^|[\x08\\W])', '[\x08\\W]'),
            ('proper_object', ['self'],
             '(^|[^\\.\\w])??(?<!\w|\\.)',
             '[\\x08\\W]+?'),
            ('keyword', kwlist, '(^|[\x08\\W])',
             '[\x08\\W]'),
            ('builtin', dir(builtins),
             '(^|[^\\.\\w])??(?<!\w|\\.)', '[\x08\\W]'),
            ('operators', ['\\+', '\\=', '\\-', '\\<', '\\>', '\\!='])
        ]
    }
}
