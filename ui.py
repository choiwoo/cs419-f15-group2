# Filename: ui.py
# Creation Date: Thu 05 Nov 2015
# Last Modified: Mon 09 Nov 2015 04:52:57 PM MST
# Author: Brett Fedack


from uiframework import (
    UI, Widget, DatasigTranslator, Form,
    Button, NumericField, SelectField, StatusLine, Tab, Text, TextField
)


# ASCII Text Generator: http://patorjk.com/software/taag/
title_string = '''\
  ____               _                      _
 / ___|   _ _ __ ___(_)_ __   __ _     __ _| |_
| |  | | | | '__/ __| | '_ \ / _` |   / _` | __|
| |__| |_| | |  \__ \ | | | | (_| |  | (_| | |_
 \____\__,_|_|  |___/_|_| |_|\__, |   \__,_|\__|
|  _ \  __ _| |_ __ _| |__   |___/___  ___  ___
| | | |/ _` | __/ _` | '_ \ / _` / __|/ _ \/ __|
| |_| | (_| | || (_| | |_) | (_| \__ \  __/\__ \\
|____/ \__,_|\__\__,_|_.__/ \__,_|___/\___||___/

 By: Woo Choi, Eric Christensen, & Brett Fedack

Usage: Tab.........Next,    Shift+Tab...Previous
       Enter.......Descend, Esc.........Back\
'''


# Color Palette (RGB Values)
dark = (0.15, 0.15, 0.15)
medium = (0.4, 0.4, 0.4)
light = (0.7, 0.7, 0.7)
red = (1.0, 0.15, 0.15)
rust = (1.0, 0.25, 0.0)
amber = (1.0, 0.6, 0.25)
yellow = (1.0, 1.0, 0.4)
cyan = (0.25, 1.0, 0.5)
blue = (0.4, 0.6, 1.0)
violet = (0.67, 0.33, 1.0)


# UI Theme
theme = {
    'default': {
        'border': (light, dark),
        'cursor': (dark, dark),
        'error': (red, dark),
        'fill': (dark, dark),
        'highlight': (light, dark),
        'inactive': (light, dark),
        'label': (light, dark),
        'selection': (light, dark),
        'status': (yellow, dark),
        'success': (blue, dark),
        'tab_active': (light, dark),
        'tab_inactive': (light, dark),
        'text': (light, dark),
        'title': (blue, dark)
    },
    'focused': {
        'border': (cyan, dark),
        'cursor': (cyan, dark, 'REVERSE'),
        'error': (red, dark),
        'fill': (dark, dark),
        'highlight': (cyan, dark, 'BOLD', 'REVERSE'),
        'inactive': (light, dark),
        'label': (cyan, dark),
        'selection': (cyan, dark, 'BOLD'),
        'status': (amber, dark),
        'success': (blue, dark),
        'tab_active': (cyan, dark),
        'tab_inactive': (light, dark),
        'text': (cyan, dark),
        'title': (blue, dark)
    },
    'disabled': {
        'border': (medium, dark),
        'cursor': (dark, dark),
        'error': (medium, dark),
        'fill': (dark, dark),
        'highlight': (medium, dark),
        'inactive': (medium, dark),
        'label': (medium, dark),
        'selection': (medium, dark),
        'status': (medium, dark),
        'success': (medium, dark),
        'tab_active': (medium, dark),
        'tab_inactive': (medium, dark),
        'text': (medium, dark),
        'title': (medium , dark)
    }
}


def build_ui(signal_router = None):
    '''
    Builds the user interface

    Parameters:
        signal_router (SignalRouter): Communication hub for the user interface
            (Optional)

    Returns:
        UI: User interface object
    '''
    ui = UI(signal_router)
    Widget.theme.load(theme)

    root = ui.root
    root.resize(80, 24)
    root.add_signal_handler('UI_UPDATE_STATUS', root.flush)
    root.add_signal_handler('UI_PROMPT_CONFIRM', root.flush)
    root.add_signal_handler('UI_FEEDBACK', root.flush)
    root.add_signal_handler('UI_DATABASE_LIST', root.flush)
    root.add_signal_handler('UI_TABLE_LIST', root.flush)

    home = build_home_tab(root)
    server = build_server_tab(root)
    database = build_database_tab(root)
    table = build_table_tab(root)
    sql = build_sql_tab(root)

    status = StatusLine('Status', root)
    status.resize(80, 3)
    status.move(0, 21)

    return ui


def build_home_tab(parent):
    '''
    Builds "Home" tab subtree of widgets

    Parameters:
        parent (Widget): Parent widget of tab subtree

    Returns:
        Widget: Subtree of widgets
    '''
    home = Tab('Home', parent, ord('h'))
    home.resize(height = 22)

    title = Text('Title', home, style = 'title')
    title.add_raw(title_string)
    title.resize(48, 14)
    title.align('CENTER')
    title.offset(0, 3)

    translator = DatasigTranslator(home)
    translator.map_output('UI_PROMPT_CONFIRM')

    form = Form(
        translator,
        prompt = 'Are you sure you want to exit? Long messages auto scroll like a news crawler.',
        sigconfirm = 'UI_EXIT'
    )

    translator = DatasigTranslator(form)
    translator.map_output('UI_SUBMIT')

    exit = Button('Exit', translator, ord('e'))
    exit.align('CENTER')
    exit.offset(0, 18)

    return home


def build_server_tab(parent):
    '''
    Builds "Server" tab subtree of widgets

    Parameters:
        parent (Widget): Parent widget of tab subtree

    Returns:
        Widget: Subtree of widgets
    '''
    offset = [0, 3]
    input_field_size = 30
    button_offset = 25

    server = Tab('Server', parent, ord('s'))
    server.resize(height = 22)

    translator = DatasigTranslator(server)
    translator.map_output('DB_CONNECT')

    form = Form(
        translator,
        hostname = None, port = None, username = None, password = None
    )

    translator = DatasigTranslator(form)
    translator.map_output('DATASIG_OUT', text = 'hostname')

    hostname = TextField('Host Name', translator, ord('h'))
    hostname.resize(width = input_field_size)
    hostname.align('CENTER')
    hostname.offset(*offset)

    translator = DatasigTranslator(form)
    translator.map_output('DATASIG_OUT', number = 'port')

    port = NumericField('Port Number', translator, ord('n'))
    port.resize(width = input_field_size)
    port.align('CENTER')
    port.move(y = 3)
    port.offset(*offset)

    translator = DatasigTranslator(form)
    translator.map_output('DATASIG_OUT', text = 'username')

    username = TextField('User Name', translator, ord('u'))
    username.resize(width = input_field_size)
    username.align('CENTER')
    username.move (y = 6)
    username.offset(*offset)

    translator = DatasigTranslator(form)
    translator.map_output('DATASIG_OUT', text = 'password')

    password = TextField('Password', translator, ord('p'))
    password.resize(width = input_field_size)
    password.align('CENTER')
    password.move (y = 9)
    password.offset(*offset)
    password.obscure()

    translator = DatasigTranslator(form)
    translator.map_output('UI_SUBMIT')

    offset[0] = button_offset
    connect = Button('Connect', translator, ord('c'))
    connect.move(y = 13)
    connect.offset(*offset)

    translator = DatasigTranslator(server)
    translator.map_output('DB_DISCONNECT')

    offset[0] += 16
    disconnect = Button('Disconnect', translator, ord('d'))
    disconnect.move(y = 13)
    disconnect.offset(*offset)

    return server


def build_database_tab(parent):
    '''
    Builds "Database" tab subtree of widgets

    Parameters:
        parent (Widget): Parent widget of tab subtree

    Returns:
        Widget: Subtree of widgets
    '''
    database = Tab('Database', parent, ord('d'))
    database.resize(height = 22)

    translator = DatasigTranslator(database)
    translator.map_input('UI_DATABASE_LIST', databases = 'options')
    translator.map_output('DB_SET_DATABASE', option = 'database')
    translator.map_request('DB_LIST_DATABASES')

    select_database = SelectField('Select Database', translator, ord('s'))
    select_database.auto_expand()
    select_database.limit_options(5)
    select_database.resize(width = 30)
    select_database.align('CENTER')
    select_database.offset(y = 3)

    commands = SelectField('Commands', database, ord('c'))
    commands.auto_expand()
    commands.limit_options(5)
    commands.resize(width = 30)
    commands.align('CENTER')
    commands.offset(y = 6)
    commands.load_options([
        'Create',
        'Delete',
        'Import',
        'Export'
    ])

    return database


def build_table_tab(parent):
    '''
    Builds "Table" tab subtree of widgets

    Parameters:
        parent (Widget): Parent widget of tab subtree

    Returns:
        Widget: Subtree of widgets
    '''
    table = Tab('Table', parent, ord('t'))
    table.resize(height = 22)

    translator = DatasigTranslator(table)
    translator.map_input('UI_TABLE_LIST', tables = 'options')
    translator.map_output('DB_SET_TABLE', option = 'table')
    translator.map_request('DB_LIST_TABLES')

    select_tables = SelectField('Select Table', translator, ord('s'))
    select_tables.auto_expand()
    select_tables.limit_options(5)
    select_tables.resize(width = 30)
    select_tables.align('CENTER')
    select_tables.offset(y = 3)

    commands = SelectField('Commands', table, ord('c'))
    commands.auto_expand()
    commands.limit_options(5)
    commands.resize(width = 30)
    commands.align('CENTER')
    commands.offset(y = 6)
    commands.load_options([
        'View Content',
        'View Schema'
    ])

    return table


def build_sql_tab(parent):
    '''
    Builds "SQL" tab subtree of widgets

    Parameters:
        parent (Widget): Parent widget of tab subtree

    Returns:
        Widget: Subtree of widgets
    '''
    sql = Tab('SQL', parent, ord('q'))
    sql.resize(height = 22)
    return sql
