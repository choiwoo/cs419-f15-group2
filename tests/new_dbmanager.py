import signals
import peewee
import psycopg2
import subprocess
import os
import sys
import itertools


class db(object):
        '''
    Database class that acts as a container for database properties
    Attributes:
		_name (str): Name of the database
		_username (str):Username for login to database server
		_password (str): Password to for database server login
        _hostname (str): Name of host machine on which the server is located
        _portnum (int): Port number identifying server on the host machine
		_table_list (str): List of all tables currently listed in the database
        _db_state (connect): connect object from psycopg2
    '''

	newid = itertools.count().next #generates new thread-safe value

    def __init__(self,**kwargs):

	    '''id should actually be self generated, need to determine a method for
		effectively doing so http://stackoverflow.com/questions/1045344/how-do-you-create-an-incremental-id-in-a-python-class'''

	    self._id = resource_cl.newid()	#applies value to get a unique object id

        if 'name' in kwargs:
            self._name = name
        else:
            self._name=""

        if 'password' in kwargs:
            self._password = password
        else:
            self._password=""

        if 'username' in kwargs:
            self._username = username
        else:
            self._username = ""

        if 'hostname' in kwargs:
            self._hostname = hostname
        else:
            self._hostname = 127.0.0.1 #initialized to default if no value provided

        if 'portnum' in kwargs:
            self._portnum = portnum
        else:
            self._portnum = 2222 #same as hostname

		self._table_list = []

	#Getters

    def getid(self):
        return self_.id

    def getname(self):
        return self._name

    def getpassword(self):
        return self._password

    def getusername(self):
        return self._username

    def gethostname(self):
        return self._hostname

    def getportnum(self):
        return self._portnum

	#Setters

    def _setid(self,value):
	self._id=value

    def setname(self,value):
        self._name= value

    def setusername(self,value):
        self._username= value

    def setpassword(self,value):
        self._password=value

    def sethostname(self,value):
        self._hostname= value

    def setportnum(self,value):
        self._portnum= value

    #Deleters

    def delid(self):
        del self._id

    def delname(self):
        del self._name

    def delusername(self):
        del self._username

    def delpassword(self):
        del self._password

    def delhostname(self):
        del self._hostname

    def delportnum(self):
        del self._portnum

    #Make getters and setters property values of db class
    id = property(getid,setid,delid,"Unique id")
    name = property(getname,setname,delname,"Database name")
    username = property(getusername,setusername,delusername,"User name")
    password = property(getpassword,setpassword,delpassword,"Password")
    hostname = property(gethostname,sethostname,delhostname,"Host name")
    portnum = property(getportnum,setportnum,delportnum,"port number")

    #List methods
    def addTable(self,table_name):
	'''Appends the given table name to the current table list'''

        self._db_list.append(table_name)
        return True

    def addTableAll(self,table_names):

	'''Adds all table names to the currently held table list'''

        for i in table_list:
            self._table_list.append(table_names[i])
        return True

    def updateTable(self,table_pre,table_post):

	'''Changes the name of a table currently stored in the table list
	from table_pre to table_post'''

        for i in self._table_list:
            if self._table_list[i] == table_pre:
                self._table_list = table_post
                return True
            else:
                return False

        return True

    def delTable(self,table_name):

	'''IF the table name exists in the table list it removes that table
	name entry and returns true, if it does not returns false'''

        for i in self._table_list:
            if self._table_list[i] == table_name:
                self._table_list.remove(table_name)
                return True
            else:
                return False

    def delTableAll(self):

	'''Deletes all table names currently stored in table_list'''

        self._table_list.clear()
            return True


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
        self._connected = False
        self._database_curr = ''
		self._database_state = ''
        self._table_curr = ''
		self._database_list = []


        # Setup signal handling.
        self._add_signal_handler('DB_CONNECT', self.connect_handler)
        self._add_signal_handler('DB_CONNECT_NEW',self.create_connection_handler)
        self._add_signal_handler('DB_DISCONNECT', self.disconnect_handler)
        self._add_signal_handler('DB_LIST_DATABASES', self.list_databases)
        self._add_signal_handler('DB_LIST_TABLES', self.list_tables)
        self._add_signal_handler('DB_IMPORT',self.import_handler)
        self._add_signal_handler('DB_EXPORT',self.export_handler)
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



    def connect_handler(self, dbname, username, password, hostname, **kwargs):
        print("Connect handler runs")
        try:
            db=dbname
            user=username
            vpass=password
            host=hostname

            if 'port' in kwargs:
                vport = kwargs['port']

                if vport is not None:
                    psql_db = psycopg2.connect(dbname=db,user=user,password=vpass,host=host,port=vport)
            else:
                psql_db = psycopg2.connect(dbname=db,user=user,password=vpass,host=host)
            print("Connect handler, connects")
        except NameError as e:
            self._msg_handler("Key error at %s"%( str(e)),True)
            print("Name error %s"%(str(e)))
            return False
        except psycopg2.Error as e:
            self._msg_handler("Connection error %s"%( str(e)),True)
            print("Connection error %s"%(str(e)))
            return False

        _connected=True

        return _connected


    def connect_handlerv2(self,dbid, **kwargs):

		#change to id??
        for i in db_list:
            if db_list[i].id == dbid
                self._curr_db = db_list[i]
                break
        else:
            self._msg_handler(message="Could not find database in list",error=True)
            #database not found in database list, send signal back for creating a new db
            return False

        dbname = self._curr_db.name
        username = self._curr_db.username
        password = self._curr_db.password
        hostname = self._curr_db.hostname

        try:
            if self._curr_db.portnum is not None:
                portnum = self._curr_db.portnum
                psql_db = psycopg2.connect(dbname=dbname,user=username,password=password,host=hostname,port=portnum)
            else:
                psql_db = psycopg2.connect(dbname=dbname,user=username,password=password,host=hostname)
        except psycopg2.Error as e:
            self._msg_handler("Connection error %s"%( str(e)),True)
            print("Connection error %s"%(str(e)))
            return False

        return True

    def create_connection_handler(self, dbname, username, password, hostname, **kwargs):

        for i in db_list:
            if db_list[i].name == name:
                self._msg_handler("That database already exists",error=True)
		connect_handlerv2(db_list[i].id)
                return False

        else:

            try:
                new_db = db(dbname,username,password,hostname)

                if 'port' in kwargs:
                    new_db.portnum = port



            except AttributeError as e:
                self._msg_handler("Connection creation failed %s"%(str(e)),error=True)

            if connect_handlerv2(new_db.id): #call the connect handler to initiate a connection??
	        db_list.append(new_db)
		self._msg_handler("Connection created for %s, now connected"%(dbname),error=False)
	    else:
                self._msg_handler("Could not create new database connection for db %s"%dbname,error=True)

        return True


    def _msg_handler(self, message, error, **kwargs):

        '''
        Emits a message signal to UI
        Parameters:
            message_text (str): Text of message
        Return
        '''
        try:
            message = message
            self._emit("UI_FEEDBACK",message=message,error=error)
        except NameError as e:
            self._emit("UI_FEEDBACK","Message handler failed %s"%(str(e)),True)


        return

    def import_handler(self, servername, username, pathname, filename, **kwargs):
        db_table = ""

        try:
            db_user = username
            db_name = servername
            path_name = pathname
            file_name = filename

            location = r"%s/%s"%(path_name,file_name)
            print("Importing database %s from %s"%(db_name,location))

            if 'table' in kwargs:
                db_table = kwargs['table']

                if db_table is not None:
                    ps = subprocess.Popen(['pg_restore','-U',db_user,'-t',db_table,'-w','-d',db_name,location],stdout=subprocess.PIPE)
            else:
                ps = subprocess.Popen(['pg_restore','-U',db_user,'-w','-d',db_name,location],stdout=subprocess.PIPE)
        except NameError as e:
            print("Name error %s"%(str(e)))
        except OSError as e:
            print("Sub process error %s"%(str(e.child_traceback)))
        except ValueError as e:
            print("Error passing args %s"%(str(e.child_traceback)))
        return True


    def export_handler(self, servername, username, pathname, filename, **kwargs):
        db_table = ""

        try:
            db_user = username
            db_name = servername
            path_name = pathname
            file_name = filename

            destination = r"%s/%s"%(path_name,file_name)
            print("Importing database %s from %s"%(db_name,destination))

            if 'table' in kwargs:
                db_table = kwargs['table']

                if db_table is not None:
                    ps = subprocess.Popen(['pg_dump','-U',db_user,'-t',db_table,'-Fc','-w','-d',db_name,'-f',destination],stdout=subprocess.PIPE)
            else:
                ps = subprocess.Popen(['pg_dump','-U',db_user,'-Fc','-w','-d',db_name,'-f',destination],stdout=subprocess.PIPE)
        except NameError as e:
            print("Name error %s"%(str(e)))
        except OSError as e:
            print("Sub process error %s"%(str(e.child_traceback)))
        except ValueError as e:
            print("Error passing args %s"%(str(e.child_traceback)))
        return True


    def disconnect_handler(self, **kwargs):
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

        # Unset database if unspecified.
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

        # Unset table if unspecified.
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
