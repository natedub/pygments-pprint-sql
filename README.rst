SQL Pretty Printer for Pygments
===============================

Use this Pygments plugin alongside your usual SQL lexer and any output
formatter to have your SQL queries reformatted for improved readability.

This filter modifies the stream of tokens that Pygments produces by
inserting whitespace at key points to make the structure of the query
more obvious.

Usage
-----

For programmatic usage, add the filter to your lexer before highlighting::

    from pygments import highlight, lexers, formatters
    from pygments_pprint_sql import SqlFilter

    lexer = lexers.MySqlLexer()
    lexer.add_filter(SqlFilter())
    print highlight(text, lexer, formatters.TerminalFormatter())

This plugin is also compatible with the pygmentize CLI tool, via the -F option::

    pygmentize -F pprint-sql script.sql

Notes
-----

DDL statements like CREATE and ALTER are left unformatted because formatting
them reliably would be a significant undertaking, especially for all flavours
of SQL.

I've done my testing with queries from an application I work on that
uses MySQL. In general it should transfer nicely to other RDBMS but I
can make no guarantees.

Patches always welcome, provided they come with test cases!
