# Filename: ui.py
# Creation Date: Thu 05 Nov 2015
# Last Modified: Wed 09 Dec 2015 10:16:17 AM MST
# Author: Brett Fedack


from uiframework import (
    signals,

    UI, Widget, DatasigTranslator, Form, Group,

    Button, FlipSwitch, NavList, NumericField, SelectField, StatusLine, Tab,
    Table, Text, TextBox, TextField, VertTab
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
        'cursor': (light, dark),
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
        'cursor': (medium, dark),
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
    root.add_signal_handler('UI_SET_DATABASE', root.flush)
    root.add_signal_handler('UI_SET_TABLE', root.flush)
    root.add_signal_handler('UI_TABLE_CONTENT', root.flush)
    root.add_signal_handler('UI_TABLE_STRUCTURE', root.flush)
    root.add_signal_handler('UI_RAW_QUERY', root.flush)

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
        prompt = 'Are you sure you want to exit?',
        sigconfirm = signals.Signal('UI_EXIT')
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
    hostname.linked_label.embellish(suffix = ': ').to_center(cross = True).shift(-1)

    translator = DatasigTranslator(form)
    translator.map_output('DATASIG_OUT', number = 'port')

    port = NumericField('Port Number', translator, ord('n'))
    port.resize(width = input_field_size)
    port.align('CENTER')
    port.move(y = 3)
    port.offset(*offset)
    port.linked_label.embellish(suffix = ': ').to_center(cross = True).shift(-1)

    translator = DatasigTranslator(form)
    translator.map_output('DATASIG_OUT', text = 'username')

    username = TextField('User Name', translator, ord('u'))
    username.resize(width = input_field_size)
    username.align('CENTER')
    username.move (y = 6)
    username.offset(*offset)
    username.linked_label.embellish(suffix = ': ').to_center(cross = True).shift(-1)

    translator = DatasigTranslator(form)
    translator.map_output('DATASIG_OUT', text = 'password')

    password = TextField('Password', translator, ord('p'))
    password.resize(width = input_field_size)
    password.align('CENTER')
    password.move (y = 9)
    password.offset(*offset)
    password.obscure()
    password.linked_label.embellish(suffix = ': ').to_center(cross = True).shift(-1)

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
    database_group = database.content_region

    translator = DatasigTranslator(database_group)
    translator.map_input('UI_DATABASE_LIST', databases = 'options')
    translator.map_output('DB_SET_DATABASE', option = 'database')
    translator.map_request('DB_LIST_DATABASES')

    database_list = SelectField('Database List', translator, ord('d'))
    database_list.auto_expand()
    database_list.resize(width = 30)
    database_list.align('CENTER')
    database_list.linked_label.embellish(suffix = ': ').to_center(cross = True).shift(-1)

    tab_group = database.content_region.scale(height = -3).offset(y = 3)

    import_tab = VertTab('Import', tab_group, ord('i'))
    export_tab = VertTab('Export', tab_group, ord('e'))

    import_tab_group = import_tab.content_region
    export_tab_group = export_tab.content_region

    translator = DatasigTranslator(import_tab_group)
    translator.map_output('DB_IMPORT_DATABASE')

    form = Form(
        translator,
        path = '', filename = '', overwrite = False
    )

    translator = DatasigTranslator(form)
    translator.map_output('DATASIG_OUT', text = 'pathname')

    import_path = TextField('Path', translator, ord('p'))
    import_path.scale(width = -12).offset(x = 12)
    import_path.linked_label.embellish(suffix = ': ').to_center(cross = True).shift(-1)

    translator = DatasigTranslator(form)
    translator.map_output('DATASIG_OUT', text = 'filename')

    import_file = TextField('Filename', translator, ord('f'))
    import_file.scale(width = -12).offset(12, 3)
    import_file.linked_label.embellish(suffix = ': ').to_center(cross = True).shift(-1)

    translator = DatasigTranslator(form)
    translator.map_output('DATASIG_OUT', enabled = 'clean')

    overwrite = FlipSwitch('Overwrite Existing', translator, ord('o'))
    overwrite.offset(32, 6)
    overwrite.linked_label.embellish(suffix = ': ').to_center(cross = True).shift(-1)

    translator = DatasigTranslator(form)
    translator.map_output('UI_SUBMIT')

    import_button = Button('Import', translator, ord('i'))
    import_button.offset(12, 10)

    translator = DatasigTranslator(export_tab_group)
    translator.map_output('DB_EXPORT_DATABASE')

    form = Form(
        translator,
        path = '', filename = '', plain = False, schema = False
    )

    translator = DatasigTranslator(form)
    translator.map_output('DATASIG_OUT', text = 'pathname')

    export_path = TextField('Path', translator, ord('p'))
    export_path.scale(width = -12).offset(x = 12)
    export_path.linked_label.embellish(suffix = ': ').to_center(cross = True).shift(-1)

    translator = DatasigTranslator(form)
    translator.map_output('DATASIG_OUT', text = 'filename')

    export_file = TextField('Filename', translator, ord('f'))
    export_file.scale(width = -12).offset(12, 3)
    export_file.linked_label.embellish(suffix = ': ').to_center(cross = True).shift(-1)

    translator = DatasigTranslator(form)
    translator.map_output('DATASIG_OUT', enabled = 'plain')

    plaintext = FlipSwitch('Plain Text', translator, ord('t'))
    plaintext.offset(24, 6)
    plaintext.linked_label.embellish(suffix = ': ').to_center(cross = True).shift(-1)

    translator = DatasigTranslator(form)
    translator.map_output('DATASIG_OUT', enabled = 'schema')

    schema_only = FlipSwitch('Schema Only', translator, ord('s'))
    schema_only.offset(50, 6)
    schema_only.linked_label.embellish(suffix = ': ').to_center(cross = True).shift(-1)

    translator = DatasigTranslator(form)
    translator.map_output('UI_SUBMIT')

    export_button = Button('Export', translator, ord('e'))
    export_button.offset(12, 10)

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
    table_group = table.content_region

    translator = DatasigTranslator(table_group)
    translator.map_input('UI_TABLE_LIST', tables = 'options')
    translator.map_output('DB_SET_TABLE', option = 'table')
    translator.map_request('DB_LIST_TABLES')

    table_list = SelectField('Table List', translator, ord('t'))
    table_list.auto_expand()
    table_list.limit_options(5)
    table_list.resize(width = 30)
    table_list.align('CENTER')
    table_list.linked_label.embellish(suffix = ': ').to_center(cross = True).shift(-1)

    tab_group = table.content_region.scale(height = -3).offset(y = 3)

    content_tab = VertTab('Content', tab_group, ord('c'))
    structure_tab = VertTab('Structure', tab_group, ord('s'))

    content_tab_group = content_tab.content_region
    content_tab_group.outset(1).scale(width = -2).offset(x = 2)

    structure_tab_group = structure_tab.content_region
    structure_tab_group.outset(1).scale(width = -2).offset(x = 2)

    translator = DatasigTranslator(content_tab_group)
    translator.map_input('UI_TABLE_CONTENT', table_content = 'table')
    translator.map_request('DB_TABLE_CONTENT')

    table_content = Table('Inspect Table', translator, ord('i'))
    table_content.linked_label.hide()
    table_content.add_signal_handler('UI_SET_TABLE', table_content.request)

    translator = DatasigTranslator(structure_tab_group)
    translator.map_input('UI_TABLE_STRUCTURE', table_structure = 'table')
    translator.map_request('DB_TABLE_STRUCTURE')

    table_structure = Table('Inspect Table', translator, ord('i'))
    table_structure.linked_label.hide()
    table_structure.add_signal_handler('UI_SET_TABLE', table_structure.request)

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

    input_group = sql.content_region
    input_group.scale(width = -38)

    translator = DatasigTranslator(input_group)
    translator.map_output('DB_RAW_QUERY', text = 'raw')

    form = Form(translator, text = '')

    text_in = TextBox('Input', form, ord('i'))
    text_in.scale(height = -2)
    text_in.linked_label.embellish(' ', ' ').offset(x = 2)

    translator = DatasigTranslator(form)
    translator.map_output('UI_SUBMIT')

    submit = Button('Submit', translator, ord('s'))
    submit.move(y = 16)

    translator = DatasigTranslator(form)
    translator.map_output('UI_CLEAR_FORM')

    reset = Button('Reset', translator, ord('r'))
    reset.move(x = 12, y = 16)

    output_group = sql.content_region
    output_group.scale(width = -38).offset(x = 38)

    form = Form(output_group)

    translator = DatasigTranslator(form)
    translator.map_input('UI_RAW_QUERY', result = 'text')
    translator.map_focus('UI_RAW_QUERY')

    text_out = TextBox('Output', translator, ord('o'))
    text_out.read_only()
    text_out.scale(height = -2)
    text_out.linked_label.embellish(' ', ' ').offset(x = 2)

    translator = DatasigTranslator(form)
    translator.map_output('UI_CLEAR_FORM')

    clear = Button('Clear', translator, ord('c'))
    clear.move(y = 16)

    return sql
