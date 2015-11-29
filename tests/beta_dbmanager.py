# Filename: mock_dbmanager.py
# Creation Date: Tue 13 Oct 2015
# Last Modified: Sun 2 Nov 2015 10:10:00 AM PST
# Author: Brett Fedack, Woo Choi

# NOTE: Significant errors on list_tables_content and list_table_structure
#       when used with UI.
#       Raw query doesn't work with UI either.
#       They all work when tested separatedly.

from uiframework import signals
# for Testing
#import signals
import psycopg2

# NOTE: By convention, signals with "UI_" prefix are sent to the user
# interface, and those with "DB_" prefix are received by this component.

class DatabaseManager():
    '''
    Database manager class that exposes both method-based and signal-based
    public interfaces for communicating with other system components

    Attributes:
        _signal_router (SignalRouter): Router for signals dispatched from/to
            this component
        _registration_log (list<2-tuple<str, method|function>>): Log of
            registered signal-handler pairs
        _hostname (str): Name of host machine on which the server is located
        _port (int): Port number identifying server on the host machine
        _username (str): Username for server login
        _password (str): Password for server login
        _dbname (str): Name of current database
        _connected (bool): Flag indicating if component is connect to a server
        _database_curr (str): Name of currently selected database
        _table_curr (str): Name of currently selected table
        _database_state (connect): psycopg2 connect object
    '''
    def __init__(self, signal_router = None):
        '''
        Parameters:
            signal_router (SignalRouter): Signal router to use for this
                component (Optional)
        '''
        # Associate a signal router with this component.
        self._signal_router = signal_router if signal_router else signals.SignalRouter()
        self._registration_log = []

        # Initialize attributes.
        self._hostname = ''
        self._port = 5432 # PostgreSQL default
        self._dbname = ''
        self._username = ''
        self._password = ''
        self._connected = False
        self._database_curr = ''
        self._table_curr = ''
        self._database_state = ''

        # Setup signal handling.
        self._add_signal_handler('DB_CONNECT', self.connect)
        self._add_signal_handler('DB_DISCONNECT', self.disconnect)
        self._add_signal_handler('DB_LIST_DATABASES', self.list_databases)
        self._add_signal_handler('DB_LIST_TABLES', self.list_tables)
        self._add_signal_handler('DB_SET_DATABASE', self.set_database)
        self._add_signal_handler('DB_SET_TABLE', self.set_table)
        self._add_signal_handler('DB_TABLE_CONTENT', self.list_table_content)
        self._add_signal_handler('DB_TABLE_STRUCTURE', self.list_table_structure)
        self._add_signal_handler('DB_RAW_QUERY', self.query_raw)


    def __del__(self):
        ''' Deregisters signal handlers before destroying this component '''
        for signame, handler in self._registration_log:
            self._signal_router.deregister(signame, handler)


    def _add_signal_handler(self, signame, handler):
        '''
        Registers signal handlers with the signal router & logs event

        Parameters:
            signame (str): Signal name
            handler (method|function): Signal handler
        '''
        registered = self._signal_router.register(signame, handler)
        if registered:
            self._registration_log.append((signame, handler))


    def _emit(self, signame, **kwargs):
        '''
        Builds a signal from given data and dispatches it to the signal router

        Parameters:
            signame (str): Signal name
            **kwargs: Signal data

        Returns:
            True if signal was handled; False otherwise
        '''
        signal = signals.Signal(signame, kwargs)
        return self._signal_router.forward(signal)


    def _emit_error(self, error_message):
        '''
        Emits a signal containing feedback for the UI in response to an error

        Parameters:
            error_message (str): Message indicating an error
        '''
        self._emit('UI_FEEDBACK', message = error_message, error = True)


    def _emit_success(self, success_message):
        '''
        Emits a signal containing feedback for the UI in response to success

        Parameters:
            error_message (str): Message indicating success
        '''
        self._emit('UI_FEEDBACK', message = success_message, error = False)


    def connect(self, hostname, port, username, password, **kwargs):
        '''
        Establishes a connection with the given server

        Parameters:
            hostname (str): Name of host machine on which the server is located
            port (int): Port number identifying server on the host machine
            username (str): Username for server login
            password (str): Password for server login

        Returns:
            bool: True if connection established; False otherwise
        '''
        # Validate inputs & component state.
        if not hostname:
            self._emit_error('Hostname must be specified')
            return False
        if not port:
            self._emit_error('Port number must be specified')
            return False

        # NOTE: Assume all other arguments are optional for the sake of this mock-up.

        # Connect to server.
        try:
            # Store connection state internally.
            self._username = username
            self._password = password
            self._hostname = hostname
            self._port = port

            # Attempt to connect
            psql_db = psycopg2.connect(user=self._username,
	           password=self._password,host=self._hostname,port=self._port)

            # Set below if connection is successful
            self._connected = True
            self._database_state = psql_db

        except NameError as e:
            #print("Name error %s"%(str(e)))
            self._emit_error('Name error %s'%(str(e)))
            return False
        except psycopg2.Error as e:
            #print("Connection error %s"%(str(e)))
            self._emit_error('Connection error %s'%(str(e)))
            return False

        # Inform the system of success.
        self._emit_success('Connection with server established')
	    # Testing
        # print("Connection success")
        return True


    def disconnect(self, **kwargs):
        '''
        Disconnects from the current server

        Returns:
            bool: True if connection terminated; False otherwise
        '''
        # Validate inputs & component state.
        if not self._connected:
            self._emit_error('Not connected to a server')
            return False

        if not self._database_state:
            self._emit_error('Not connected to a server')
            self._connected = False
            return False

        # Disconnect from the current server.
        try:
            self._database_state.close()
        except:
            self._emit_error('Disconnect failed')
            return False

        # Store connection state internally.
        self._connected = False
        self._database_curr = ''
        self._table_curr = ''
        self._database_state = ''
        # Inform the system of success.
        self._emit_success('Connection with server terminated')

        # Testing
        #print("Disconnect worked")
        return True


    def import_db(self, path, filetype, **kwargs):
        '''
        Imports a database from the given file

        Parameters:
            path (str): Path to input file
            filetype (str): Format of input file

        Returns:
            True if a new database is created; False otherwise
        '''
        # Validate inputs & component state.
        if not self._connected:
            self._emit_error('Not connected to a server')
            return False

        # Import given file.
        # TODO: Peewee stuff

        # Inform system of success.
        self._emit_success('Database successfully imported from file')


    def export_db(self, path, filetype, **kwargs):
        '''
        Exports current database to the given file

        Parameters:
            path (str): Path to output file
            filetype (str): Format of output file

        Returns:
            True if a new file is created; False otherwise
        '''
        # Validate inputs & component state.
        if not self._connected:
            self._emit_error('Not connected to a server')
            return False
        if not self._database_curr:
            self._emit_error('No database selected')
            return False

        # Export current database to given file.
        # TODO: Peewee stuff

        # Inform system of success.
        self._emit_success('Database successfully exported to file')


    def set_database(self, database, **kwargs):
        '''
        Designates current database on server

        Parameters:
            database (str): Identifier for database

        Returns:
            bool: True if database is set; False otherwise
        '''
        # NOTE: Mock databases are stored as a global.
        # Testing
        #print("starting set_database")
        # Unset database if unspecified.
        if database is None:
            self._database_curr = None
            self._emit_success('Database unset')
            return False

        # Validate inputs & component state.
        if not self._connected:
            self._emit_error('Not connected to a server')
            return False

        # First disconnect from current connection
        if self._database_state:
            self._database_state.close()
            self._database_state = ''
            self._connected = False
            #print("disconn worked in set db")

        # Must connect again using the provided database
        try:
            # Set the database.
            self._database_curr = database

            # Attempt connection
            psql_db = psycopg2.connect(dbname=self._database_curr,user=self._username,
            password=self._password,host=self._hostname,port=self._port)

            self._connected = True
            self._database_state = psql_db
            #print("db set connected")
        except NameError as e:
            #print("Name error %s"%(str(e)))
            self._emit_error('Name error %s'%(str(e)))
            return False
        except psycopg2.Error as e:
            #print("Connection error %s"%(str(e)))
            self._emit_error('Connection error %s'%(str(e)))
            return False

        # Inform system of success.
        self._emit('UI_SET_DATABASE', database = database)
        self._emit_success('"{}" set as current database'.format(database))

        #print(self._database_curr)
        return True


    def set_table(self, table, **kwargs):
        '''
        Designates current table in database

        Parameters:
            table (str): Identifier for table

        Returns:
            bool: True if table is set; False otherwise
        '''
        # NOTE: Mock databases are stored as a global.

        # Unset table if unspecified.
        if table is None:
            self._table_curr = None
            self._emit_success('Table unset')
            return False

        # Validate inputs & component state.
        if not self._connected:
            self._emit_error('Not connected to a server')
            return False
        if not self._database_curr:
            self._emit_error('No database selected')
            return False

        # Set the table.
        self._table_curr = table
        #print(self._table_curr)

        # Inform the system of success.
        self._emit('UI_SET_TABLE', table = table)
        self._emit_success('"{}" set as current table'.format(table))

        return True


    def list_databases(self, **kwargs):
        '''
        Queries current server for a list of database names

        Returns:
            list: List of table names
        '''
        # NOTE: Mock databases are stored as a global.

        # Validate inputs & component state.
        if not self._connected:
            self._emit_error('Not connected to a server')
            return []

        if not self._database_state:
            self._emit_error('Not connected to a server')
            return []


        # Acquire a listing of databases on the server.

        cursor = self._database_state.cursor()
        cursor.execute("SELECT datname FROM pg_database")
        records = cursor.fetchall()

        # Converting to acceptable list format
        database_list = [i[0] for i in records]

        # Testing
        #print(database_list)
        cursor.close()

        # Transmit database list.
        self._emit('UI_DATABASE_LIST', databases = database_list)

        return database_list


    def list_tables(self, **kwargs):
        '''
        Queries current database for a list of table names

        Returns:
            list: List of table names
        '''
        # NOTE: Mock databases are stored as a global.

        # Validate inputs & component state.
        if not self._connected:
            self._emit_error('Not connected to a server')
            return []
        if not self._database_curr:
            self._emit_error('No database selected')
            return []
        if not self._database_state:
            self._emit_error('No connection to database')
            return []

        # Acquire a listing of tables in the current database.
        try:
            cursor = self._database_state.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            records = cursor.fetchall()

            # Converting to acceptable format
            table_list = [i[0] for i in records]

            #print(table_list)
            cursor.close()
        except:
            self._emit_error('Error while executing table list')
            return []

        # Transmit table list.
        self._emit('UI_TABLE_LIST', tables = table_list)

        return table_list


    def list_table_content(self, **kwargs):
        '''
        Queries current table for a listing of its contents

        Returns:
            list<list>: List of table rows (first is header)
        '''
        # Validate inputs & component state.
        if not self._connected:
            self._emit_error('Not connected to a server')
            return []
        if not self._table_curr:
            self._emit_error('No table selected')
            return []
        if not self._database_state:
            self._emit_error('No connection to database')
            return []

        # Acquire a listing of the current table's contents.
        try:
            cursor = self._database_state.cursor()

            # Get row headers
            cursor_str = "SELECT column_name FROM information_schema.columns WHERE table_name=\'%s\'"%(self._table_curr)
            cursor.execute(cursor_str)
            records = cursor.fetchall()

            # Convert to acceptable list
            table_column = [i[0] for i in records]

            # Get rows
            cursor_str = "SELECT * FROM %s"%(self._table_curr)
            cursor.execute(cursor_str)
            records = cursor.fetchall()

            # Combine row headers and rows
            table_content = [table_column] + records
            # print(table_content)
            #print("table_content:")
            #print(table_content)
            # close cursor
            cursor.close()
        except:
            self._emit_error('Error while querying table content')
            return []

        # Transmit table contents.
        self._emit('UI_TABLE_CONTENT', table_content = table_content)

        return table_content


    def list_table_structure(self, **kwargs):
        '''
        Queries current table for a listing of its structure

        Returns:
            list<list>: List of table strucure (first is header)
        '''
        # Validate inputs & component state.
        if not self._connected:
            self._emit_error('Not connected to a server')
            return []
        if not self._table_curr:
            self._emit_error('No table selected')
            return []
        if not self._database_state:
            self._emit_error('No connection to database')
            return []

        # Acquire a listing of the current table's structure.
        try:
            cursor = self._database_state.cursor()
            # Query for table structure
            cursor_str = """SELECT DISTINCT c.column_name, c.data_type, c.character_maximum_length, tc.constraint_type
            FROM information_schema.table_constraints tc
            JOIN information_schema.columns AS c ON c.table_name = tc.table_name
            WHERE c.table_name = '%s';"""%(self._table_curr)
            cursor.execute(cursor_str)
            records = cursor.fetchall()

            # Fromat list<list>
            table_list = [i[0] for i in records]
            table_structure = [['Column_Name','Data_Type','Max_Length','Constraint_Type']] + records
            #print("db_table_structure:")
            #print(table_structure)
            cursor.close()
        except:
            self.emit_error('Error while executing table structure')
            return []

        # Transmit table structure.
        self._emit('UI_TABLE_STRUCTURE', table_structure = table_structure)

        return table_structure

    # Not coded
    def query_raw(self, raw, **kwargs):
        '''
        Queries current database using the given string

        Parameters:
            raw (str): Literal form of query

        Returns:
            str: Query result
        '''
        # Validate inputs & component state.
        if not self._connected:
            self._emit_error('Not connected to a server')
            return ''
        # Must be connected to a database to run queries
        if not self._database_curr:
            self._emit_error('No database selected')
            return ''
        if not self._database_state:
            self._emit_error('No connection to database')
            return ''

        # Submit raw query to the DBMS.
        try:
            cursor = self._database_state.cursor()
            cursor.execute(raw)

            try:
                records = cursor.fetchall()
                raw_query_result = records
                #print (raw_query_result)
            except:
                raw_query_result = 'query accepted'
                #print (raw_query_result)
            self._database_state.commit()
            cursor.close()
        except:
            self._emit_error('Error while executing query')
            return ''

        # Transmit query result.
        self._emit('UI_RAW_QUERY', result = raw_query_result)

        return raw_query_result
