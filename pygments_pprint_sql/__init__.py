"""
SQL Pretty Printer for Pygments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you want to automatically pretty format SQL queries for better
readability, add this :class:`SqlFilter` to the Pygments SQL lexer
of your choosing. See the README for examples.

:copyright: Copyright 2013 Nathan Wright.
:license: BSD, see LICENSE for details.

"""

from pygments.filter import Filter
from pygments.token import Keyword
from pygments.token import Punctuation
from pygments.token import Text


class SqlFilter(Filter):
    """
    Pygments stream filter that rewrites text nodes for better readability.
    """

    ddl_keywords = set([
        u'CREATE',
        u'ALTER',
        u'DROP',
    ])

    nl_keywords = set([
        u'SELECT',
        u'FROM',
        u'LEFT',
        u'RIGHT',
        u'INNER',
        u'OUTER',
        u'WHERE',
        u'HAVING',
        u'GROUP',
        u'EXISTS',
        u'UNION',
        u'AND',
        u'OR',
        u'ON',
        u'NOT',
        u'LIMIT',
        u'INSERT',
        u'UPDATE',
    ])

    def filter(self, lexer, stream):
        indent = u'    '
        depth = 0
        func_depth = 0

        # Track the last non-text token type.
        last_ttype = None

        # Buffer the last text value.
        last_text = None

        # DDL clauses are not formatted currently. Formatting is disabled
        # until a non-DDL clause is reached, so CREATE TABLE .. SELECT works.
        in_ddl = False

        wrap = False
        wrap_next = False

        for ttype, value in stream:
            # Normalize and buffer text values until the next iteration.
            if ttype in Text:
                last_text = u' '
                continue

            # Detect DDL statements beginning and ending.
            if ttype in Keyword:
                if not in_ddl and value.upper() in self.ddl_keywords:
                    in_ddl = True
                elif value == u'SELECT':
                    in_ddl = False

            # Determine if wrapping needs to occur for this token.
            if not in_ddl and last_ttype is not None:
                if wrap_next:
                    wrap = True
                    wrap_next = False

                if ttype in Keyword \
                and last_ttype not in Keyword \
                and value.upper() in self.nl_keywords:
                    wrap = True

                if ttype in Punctuation:
                    if value == u'(':
                        if last_ttype in Keyword:
                            depth += 1
                            wrap_next = True
                        else:
                            func_depth += 1
                    elif value == u')':
                        if func_depth:
                            func_depth -= 1
                        else:
                            depth -= 1
                            wrap = True

                if wrap:
                    yield Text, u'\n' + indent * depth
                    wrap = False
                    last_text = None

            if last_text is not None:
                yield Text, last_text
                last_text = None

            yield ttype, value
            last_ttype = ttype

        # Maintain standard pygments behaviour by always appending a newline.
        yield Text, u'\n'
