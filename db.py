import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


con = sqlite3.connect(':memory:')
con.row_factory = dict_factory
cur = con.cursor()
cur.execute("""
                create table users (
                    id integer primary key autoincrement, 
                    name text, 
                    password text, 
                    type int,
                    tax int,
                    ut_citizen bool
                );
                
            """)
cur.execute("""
                create table managed_by (
                    id integer primary key autoincrement, 
                    accountant_id int, 
                    user_id int
                );
            """)
con.execute("""
    create table taxes (
        id integer primary key autoincrement, 
        user_id int, 
        ammount int, 
        time  int, 
        paid bool
    );
""")
