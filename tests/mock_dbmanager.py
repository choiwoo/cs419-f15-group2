# Filename: mock_dbmanager.py
# Creation Date: Tue 13 Oct 2015
# Last Modified: Sun 15 Nov 2015 01:26:43 AM MST
# Author: Brett Fedack


from uiframework import signals
#import signals
import psycopg2
# NOTE: By convention, signals with "UI_" prefix are sent to the user
# interface, and those with "DB_" prefix are received by this component.


# Mock Database List
mock_databases = {
    'Book Store': [
        'Book', 'Genre', 'Author', 'Customer', 'Publisher', 'Inventory'
    ],
    'Car Dealership': [
        'Car', 'Make', 'Model', 'Employee', 'Customer', 'Order'
    ]
}


# Mock Raw Query Result
mock_raw_query_result ='''\
HAL: Good afternoon, gentlemen.

HAL: I am a HAL 9000 computer.

HAL: I became 'operational at the H.A.L. plant in Urbana, Illinois on the \
12th, of January 1992.

HAL: My instructor was Mr. Langley, and he taught me to sing a song.

HAL: If you\'d like to hear it I can sing it for you.

DAVE BOWMAN: Yes, I\'d like to hear it, HAL. Sing it for me.

HAL: It\'s called Daisy.

HAL: Daisy, Daisy, give me your answer do.

HAL: I\'m half crazy all for the love of you.

HAL: It won\'t be a stylish marriage, I can\'t afford a carriage.

HAL: But you\'ll look sweet upon the seat of a bicycle built for two.
'''


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
        _database_state (psycopg2.connect): psycopg2 connect class
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
        self._add_signal_handler('DB_CONNECT', self.connect_handler)
        self._add_signal_handler('DB_DISCONNECT', self.disconnect)
        self._add_signal_handler('DB_LIST_DATABASES', self.list_databases)
        self._add_signal_handler('DB_LIST_TABLES', self.list_tables)
        self._add_signal_handler('DB_SET_DATABASE', self.set_database)
        self._add_signal_handler('DB_SET_TABLE', self.set_table)
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

        # Store connection state internally.
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password
        self._connected = True

        # Connect to server.
        # TODO: Peewee stuff

        # Inform the system of success.
        self._emit_success('Connection with server established')

        return True

    def connect_handler(self, username, password, hostname, port, **kwargs):
        '''
        Establishes a connection with the given server
        Parameters:
            hostname (str): Name of host machine on which the server is located
            username (str): Username for server login
            password (str): Password for server login
            port (int): Port number identifying server on the host machine
        Returns:
            bool: True if connection established; False otherwise
        '''
        # Validate inputs & component state.
        if not hostname:
            self._emit(
                'UI_FEEDBACK',
                message = 'Hostname must be specified',
                error = True
            )
            return False

        if not port:
            self._emit(
                'UI_FEEDBACK',
                message = 'Port number must be specified',
                error = True
            )
            return False
        #print("Starting connect_handler...")
        try:
            self._username = username
            self._password = password
            self._hostname = hostname
            self._port = port

            psql_db = psycopg2.connect(user=self._username,password=self._password,
            host=self._hostname, port=self._port)


            #print("Connect_handler's attempt for connection is successful...")

            self._connected = True
            self._database_state = psql_db

        except NameError as e:
            #self._msg_handler("Key error at %s"%( str(e)),True)
            print("Name error %s"%(str(e)))
            return False
        except psycopg2.Error as e:
            #self._msg_handler("Connection error %s"%( str(e)),True)
            print("Connection error %s"%(str(e)))
            return False

        self._emit(
            'UI_FEEDBACK',
            message = 'Connection with server established',
            error = False
        )

        #print("connect_handler is now finished.\n\n")
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

        # Disconnect from the current server.
        # No error checking at the moment
        self._database_state.close()

        # Store connection state internally.
        self._connected = False

        # Inform the system of success.
        self._emit_success('Connection with server terminated')

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

        # Unset database if unspecified.
        if database is None:
            self._database_curr = None
            self._emit_success('Database unset')
            return False

        # Validate inputs & component state.
        if not self._connected:
            self._emit_error('Not connected to a server')
            return False
        #if not database in mock_databases: # TODO: Peewee stuff
        #    self._emit_error('"{}" database not found on server'.format(database))
        #    return False

        # Set the database.
        self._database_curr = database

        # First close current connection.
        self._database_state.close()

        # Reestablish connection
        # NOTE: no error checking
        psql_db = psycopg2.connect(dbname=self._database_curr, user=self._username,
        password=self._password, host=self._hostname, port=self._port)

        self._database_state = psql_db

        # Checking (test)
        #cursor = psql_db.cursor()
        #cursor.execute("SELECT current_database()")
        #records = cursor.fetchall()
        #print(records)
        #cursor.close()

        # Inform system of success.
        self._emit_success('"{}" set as current database'.format(database))

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
        if not table in mock_databases[self._database_curr]: # TODO: Peewee stuff
            self._emit_error('"{}" table not found in "{}" database'.format(
                table, self._database_curr
            ))
            return False

        # Set the table.
        self._table_curr = table

        # Inform the system of success.
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

        # Acquire a listing of databases on the server.

        cursor = self._database_state.cursor()
        cursor.execute("SELECT datname FROM pg_database")
        records = cursor.fetchall()
        database_list = list(records)
        #print(database_list)
        cursor.close()

        #database_list = list(mock_databases.keys())

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

        # Acquire a listing of tables in the current database.
        # TODO: Peewee stuff
        table_list = mock_databases[self._database_curr]

        # Transmit table list.
        self._emit('UI_TABLE_LIST', tables = table_list)

        return table_list


    def query_raw(self, raw, **kwargs):
        '''
        Queries current database using the given string

        Parameters:
            raw (str): Literal form of query

        Returns:
            str: Query result
        '''
        # NOTE: Mock raw query result is a global.

        # Validate inputs & component state.
        if not self._connected:
            self._emit_error('Not connected to a server')
            return ''

        # Submit raw query to the DBMS.
        # TODO: Peewee stuff
        # No input checking yet
        cursor = self._database_state.cursor()
        cursor.execute(raw)
        raw_result = cursor.fetchall()
        cursor.close()

        self._emit('UI_RAW_QUERY', result = raw_result)
        return raw_result

        # Transmit query result.
        #self._emit('UI_RAW_QUERY', result = mock_raw_query_result)
        #return mock_raw_query_result
