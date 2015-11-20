# Filename: mock_dbmanager.py
# Creation Date: Tue 13 Oct 2015
# Last Modified: Fri 20 Nov 2015 02:23:26 PM MST
# Author: Brett Fedack


from uiframework import signals


# NOTE: By convention, signals with "UI_" prefix are sent to the user
# interface, and those with "DB_" prefix are received by this component.


# Mock Data
mock_databases = {
    'Book Store': [
        'Book', 'Genre', 'Author', 'Customer', 'Publisher', 'Inventory'
    ],
    'Car Dealership': [
        'Car', 'Make', 'Model', 'Employee', 'Customer', 'Order'
    ]
}
mock_table_content = [
    ['Id', 'First Name', 'Surname',  'DoB'       ],
    [1,    'Linus',      'Torvalds', '1969-12-28'],
    [2,    'Richard',    'Stallman', '1953-03-16'],
    [3,    'Bill',       'Gates',    '1955-10-28'],
    [4,    'Steve',      'Jobs',     '1955-02-24'],
    [5,    'Steve',      'Wozniak',  '1950-08-11']
]
mock_table_structure = [
    ['Field',      'Type',        'Null', 'Key', 'Default',    'Extra'         ],
    ['Id',         'int(11)',     'NO',   'PRI', 'NULL',       'auto_increment'],
    ['First Name', 'varchar(20)', 'NO',   '',    '',           ''              ],
    ['Surname',    'varchar(20)', 'NO',   '',    '',           ''              ],
    ['DoB',        'date',        'NO',   '',    '0000-00-00', ''              ],
]
mock_pretty_print = '''\
+-----------+------+------------+-----------------+
| City name | Area | Population | Annual Rainfall |
+-----------+------+------------+-----------------+
| Adelaide  | 1295 |  1158259   |      600.5      |
| Brisbane  | 5905 |  1857594   |      1146.4     |
| Darwin    | 112  |   120900   |      1714.7     |
| Hobart    | 1357 |   205556   |      619.5      |
| Sydney    | 2058 |  4336374   |      1214.8     |
| Melbourne | 1566 |  3806092   |      646.9      |
| Perth     | 5386 |  1554769   |      869.4      |
+-----------+------+------------+-----------------+\
'''
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

HAL: But you\'ll look sweet upon the seat of a bicycle built for two.\
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
        # TODO: Peewee stuff

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
        if not database in mock_databases: # TODO: Peewee stuff
            self._emit_error('"{}" database not found on server'.format(database))
            return False

        # Set the database.
        self._database_curr = database

        # Inform system of success.
        self._emit('UI_SET_DATABASE', database = database)
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

        # Acquire a listing of databases on the server.
        # TODO: Peewee stuff
        database_list = list(mock_databases.keys())

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
        if not self._table_curr in mock_databases[self._database_curr]: # TODO: Peewee stuff
            self._emit_error('"{}" table not found in "{}" database'.format(
                self._table_curr, self._database_curr
            ))
            return []

        # Acquire a listing of the current table's contents.
        # TODO: Peewee stuff
        table_content = mock_table_content

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
        if not self._table_curr in mock_databases[self._database_curr]: # TODO: Peewee stuff
            self._emit_error('"{}" table not found in "{}" database'.format(
                self._table_curr, self._database_curr
            ))
            return []

        # Acquire a listing of the current table's structure.
        # TODO: Peewee stuff
        table_structure = mock_table_structure

        # Transmit table structure.
        self._emit('UI_TABLE_STRUCTURE', table_structure = table_structure)

        return table_structure


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

        # Transmit query result.
        self._emit('UI_RAW_QUERY', result = mock_raw_query_result)

        return mock_raw_query_result
