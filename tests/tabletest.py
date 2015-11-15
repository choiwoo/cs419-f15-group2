#!/bin/env python3

table = '''\
+------------+----------+------+-----+---------+----------------+
| Field      | Type     | Null | Key | Default | Extra          |
+------------+----------+------+-----+---------+----------------+
| Id         | int(11)  | NO   | PRI | NULL    | auto_increment |
| Name       | char(35) | NO   |     |         |                |
| Country    | char(3)  | NO   | UNI |         |                |
| District   | char(20) | YES  | MUL |         |                |
| Population | int(11)  | NO   |     | 0       |                |
+------------+----------+------+-----+---------+----------------+\
'''

def asciiToTable(text):
    '''
    Creates a table from ASCII "Pretty-Print" text

    Parameters:
        text (str): ASCII "Pretty-Print" representation of a table

    Returns:
        list<list<str>>: 2-dimensional list representation of a table
    '''
    # Parse "Pretty-Print" ASCII table into a tabular list.
    return [
        [item.strip() for item in row.split('|')[1:-1]]
        for row in text.split('\n')
        if row[0] == '|'
    ]

print(asciiToTable(table))

#  SELECT * FROM information_schema.columns  WHERE table_name = 'foo'
#  SELECT * FROM information_schema.table_constraints  WHERE table_name = 'foo'
