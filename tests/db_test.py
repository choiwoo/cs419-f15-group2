
# test for database manager

import psycopg2
import sys
from dbmanager import *
from signals import *
# for Testing
#import signal
import psycopg2
def main():
    print("****************************")
    print("Starting a mock demo for database\n\n\n")

    #initializing
    from_gui = SignalRouter()
    dbm = DatabaseManager(from_gui)

    #Connect
    test_sig = Signal("DB_CONNECT",data={'username':'guest01','password':'pass01','hostname':'localhost','port':5432})
    from_gui.forward(test_sig)


    #list databases
    list_db_sig = Signal("DB_LIST_DATABASES",data={})
    from_gui.forward(list_db_sig)

    #set database
    set_db_sig = Signal("DB_SET_DATABASE",data={'database':'testdb'})
    from_gui.forward(set_db_sig)

    #list tables
    list_tables_sig = Signal("DB_LIST_TABLES",data={})
    from_gui.forward(list_tables_sig)

    #set tables
    set_tables_sig = Signal("DB_SET_TABLE", data={'table':'book_store'})
    from_gui.forward(set_tables_sig)

    #list_table_content
    list_content_sig = Signal("DB_TABLE_CONTENT", data={})
    from_gui.forward(list_content_sig)

    #list_table_structure
    list_structure_sig = Signal("DB_TABLE_STRUCTURE", data={})
    from_gui.forward(list_structure_sig)

    #raw queries
    raw_query_sig = Signal("DB_RAW_QUERY",data={'raw':"INSERT INTO book_store VALUES ('book', 'gen', 'author', 'pub', 1);"})
    raw_query_sig = Signal("DB_RAW_QUERY",data={'raw':"SELECT * FROM book_store;"})

    #from_gui.forward(raw_query_sig)

    #disconnect
    disconnect_sig = Signal("DB_DISCONNECT",data={})
    from_gui.forward(disconnect_sig)

    print("Mock_db test is now finished")


if __name__ == "__main__":
    main()
