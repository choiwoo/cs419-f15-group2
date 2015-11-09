# Filename: mock_dbmanager.py
# Creation Date: Tue 13 Oct 2015
# Last Modified: Mon 09 Nov 2015 03:00:58 PM MST
# Author: Brett Fedack


from uiframework import signals


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
mock_raw_query_result = ' '.join([
    'Good afternoon, gentlemen. I am a HAL 9000 computer. I became',
    'operational at the H.A.L. plant in Urbana, Illinois on the 12th',
    'of January 1992. My instructor was Mr. Langley, and he taught me',
    'to sing a song. If you\'d like to hear it I can sing it for you.'
])


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

        # NOTE: Assume all other arguments are optional for the sake of this mock-up.

        # Connect to server.
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password
        self._connected = True
        self._emit(
            'UI_FEEDBACK',
            message = 'Connection with server established',
            error = False
        )

        return True


    def disconnect(self, **kwargs):
        '''
        Disconnects from the current server

        Returns:
            bool: True if connection terminated; False otherwise
        '''
        # Validate inputs & component state.
        if not self._connected:
            self._emit(
                'UI_FEEDBACK',
                message = 'Not connected to a server',
                error = True
            )
            return False

        # Disconnect from the current server.
        self._connected = False
        self._emit(
            'UI_FEEDBACK',
            message = 'Connection with server terminated',
            error = False
        )

        return True


    def set_database(self, database, **kwargs):
        '''
        Designates current database on server

        Parameters:
            database (str): Identifier for database

        Returns:
            bool: True if database is set; False otherwise
        '''
        # NOTE: Mock databases are stored as a global.

        # Unset database, if specified.
        if database is None:
            self._database_curr = None
            self._emit(
                'UI_FEEDBACK',
                message = 'Database unset'.format(database),
                error = False
            )
            return False

        # Validate inputs & component state.
        if not self._connected:
            self._emit(
                'UI_FEEDBACK',
                message = 'Not connected to a server',
                error = True
            )
            return False
        if not database in mock_databases:
            self._emit(
                'UI_FEEDBACK',
                message = '"{}" database not found on server'.format(database),
                error = True
            )
            return False

        # Set the database.
        self._database_curr = database
        self._emit(
            'UI_FEEDBACK',
            message = '"{}" set as current database'.format(database),
            error = False
        )

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

        # Unset table, if specified.
        if table is None:
            self._table_curr = None
            self._emit(
                'UI_FEEDBACK',
                message = 'Table unset'.format(table),
                error = False
            )
            return False

        # Validate inputs & component state.
        if not self._connected:
            self._emit(
                'UI_FEEDBACK',
                message = 'Not connected to a server',
                error = True
            )
            return False
        if not self._database_curr:
            self._emit(
                'UI_FEEDBACK',
                message = 'No database selected',
                error = True
            )
            return []
        if not table in mock_databases[self._database_curr]:
            self._emit(
                'UI_FEEDBACK',
                message = '"{}" table not found in "{}" database'.format(
                    table, self._database_curr
                ), error = True
            )
            return False

        # Set the table.
        self._table_curr = table
        self._emit(
            'UI_FEEDBACK',
            message = '"{}" set as current table'.format(table),
            error = False
        )

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
            self._emit(
                'UI_FEEDBACK',
                message = 'Not connected to a server',
                error = True
            )
            return []

        # Transmit database list.
        database_list = list(mock_databases.keys())
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
            self._emit(
                'UI_FEEDBACK',
                message = 'Not connected to a server',
                error = True
            )
            return []
        if not self._database_curr:
            self._emit(
                'UI_FEEDBACK',
                message = 'No database selected',
                error = True
            )
            return []

        # Transmit table list.
        table_list = mock_databases[self._database_curr]
        self._emit('UI_TABLE_LIST', tables = table_list)

        return table_list


    def query_raw(self, raw, **kwargs):
        '''
        Queries current database using the given string

        Returns:
            str: Query result
        '''
        # NOTE: Mock raw query result is a global.

        # Validate inputs & component state.
        if not self._connected:
            self._emit(
                'UI_FEEDBACK',
                message = 'Not connected to a server',
                error = True
            )
            return []

        # Transmit query result.
        self._emit('UI_RAW_QUERY', result = mock_raw_query_result)

        return result
