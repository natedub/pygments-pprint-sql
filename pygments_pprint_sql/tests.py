import subprocess

from unittest import TestCase

from pygments import highlight
from pygments.filters import KeywordCaseFilter
from pygments.formatters import NullFormatter
from pygments.lexers import MySqlLexer
from pygments_pprint_sql import SqlFilter


class TestSqlFormatting(TestCase):

    def highlight(self, text, upper=True):
        sql_lexer = MySqlLexer()
        if upper:
            sql_lexer.add_filter(KeywordCaseFilter(case='upper'))
        sql_lexer.add_filter(SqlFilter())
        output = highlight(text, sql_lexer, NullFormatter())
        return output

    def assertOutputEqual(self, output, expected):
        # Trim the trailing new line that Pygments adds for ease of testing,
        # but don't use str.strip() because multiple newlines are a problem.
        self.assertTrue(output, 'Output should not be empty')
        self.assertEqual(output[-1], '\n', 'Expected trailing newline')
        self.assertEqual(output[:-1], expected)

    def test_simple(self):
        sql = 'select * from users as u inner join users_groups as ug on u.id = ug.user_id where u.id = 123'
        fmt = self.highlight(sql)
        print fmt
        self.assertOutputEqual(fmt, '\n'.join([
            'SELECT *',
            'FROM users AS u',
            'INNER JOIN users_groups AS ug',
            'ON u.id = ug.user_id',
            'WHERE u.id = 123',
        ]))

    def test_simple_lower(self):
        sql = 'select * from users as u inner join users_groups as ug on u.id = ug.user_id where u.id = 123'
        fmt = self.highlight(sql, upper=False)
        print fmt
        self.assertOutputEqual(fmt, '\n'.join([
            'select *',
            'from users as u',
            'inner join users_groups as ug',
            'on u.id = ug.user_id',
            'where u.id = 123',
        ]))

    def test_create_from_select(self):
        sql = 'create temporary table users_temp select * from users as u inner join users_groups as ug on u.id = ug.user_id'
        fmt = self.highlight(sql)
        print fmt
        self.assertOutputEqual(fmt, '\n'.join([
            'CREATE temporary TABLE users_temp',
            'SELECT *',
            'FROM users AS u',
            'INNER JOIN users_groups AS ug',
            'ON u.id = ug.user_id',
        ]))

    def test_complex(self):
        sql = '''select oranges.id as oranges_id, oranges.apple_id as oranges_apple_id, oranges.user_id as oranges_user_id, oranges.group_id as oranges_group_id, oranges.role_id as oranges_role_id, oranges.created_on as oranges_created_on, oranges.modified_on as oranges_modified_on, oranges.unique_key as oranges_unique_key from oranges inner join (select oranges.user_id as user_id, oranges.group_id as group_id, substring_index(group_concat(oranges.id order by field(oranges.apple_id, %s, %s, %s)), %s, %s) as closest_id from oranges where oranges.apple_id in (%s, %s, %s) group by oranges.user_id, oranges.group_id) as anon_1 on oranges.id = anon_1.closest_id'''
        fmt = self.highlight(sql)
        print fmt
        self.assertOutputEqual(fmt, '\n'.join([
            'SELECT oranges.id AS oranges_id, oranges.apple_id AS oranges_apple_id, oranges.user_id AS oranges_user_id, oranges.group_id AS oranges_group_id, oranges.role_id AS oranges_role_id, oranges.created_on AS oranges_created_on, oranges.modified_on AS oranges_modified_on, oranges.unique_key AS oranges_unique_key',
            'FROM oranges',
            'INNER JOIN (',
            '    SELECT oranges.user_id AS user_id, oranges.group_id AS group_id, substring_index(group_concat(oranges.id ORDER BY field(oranges.apple_id, %s, %s, %s)), %s, %s) AS closest_id',
            '    FROM oranges',
            '    WHERE oranges.apple_id IN (',
            '        %s, %s, %s',
            '    )',
            '    GROUP BY oranges.user_id, oranges.group_id',
            ') AS anon_1',
            'ON oranges.id = anon_1.closest_id'
        ]))

    def test_incoming_whitespace(self):
        sql = '\n'.join([
            'SELECT apples.id AS apples_id, \n apples.name AS apples_name, apples.slug AS apples_slug, apples.created_on AS apples_created_on, apples.modified_on AS apples_modified_on, apples.restricted AS apples_restricted, apples.is_podcast AS apples_is_podcast, apples.parent_id AS apples_parent_id, apples.site_id AS apples_site_id ',
            '       FROM apples ',
            'WHERE %s = apples.site_id   ',
            '     AND apples.id = %s ',
            ' LIMIT %s',
        ])
        fmt = self.highlight(sql)
        print fmt
        self.assertOutputEqual(fmt, '\n'.join([
            'SELECT apples.id AS apples_id, apples.name AS apples_name, apples.slug AS apples_slug, apples.created_on AS apples_created_on, apples.modified_on AS apples_modified_on, apples.restricted AS apples_restricted, apples.is_podcast AS apples_is_podcast, apples.parent_id AS apples_parent_id, apples.site_id AS apples_site_id',
            'FROM apples',
            'WHERE %s = apples.site_id',
            'AND apples.id = %s',
            'LIMIT %s',
        ]))

    def test_pygmentize(self):
        # subprocess requires a fileno for stdin so StringIO won't work here,
        # echo is the next easiest thing.
        sql = 'select * from users as u inner join users_groups as ug on u.id = ug.user_id where u.id = 123'
        sql_cmd = ['echo', sql]
        pygmentize_cmd = [
            'pygmentize',
            '-l', 'mysql',
            '-F', 'pprint-sql',
            '-f', 'null',
        ]
        sql = subprocess.Popen(
            sql_cmd,
            stdout=subprocess.PIPE,
        )
        pygmentize_cmd = subprocess.Popen(
            pygmentize_cmd,
            stdin=sql.stdout,
            stdout=subprocess.PIPE,
        )
        fmt = pygmentize_cmd.communicate()[0]
        print fmt
        self.assertOutputEqual(fmt, '\n'.join([
            'select *',
            'from users as u',
            'inner join users_groups as ug',
            'on u.id = ug.user_id',
            'where u.id = 123',
        ]))
