# Filename: widgets.py
# Creation Date: Thu 08 Oct 2015
# Last Modified: Mon 09 Nov 2015 02:58:25 PM MST
# Author: Brett Fedack


import curses
import curses.ascii as ascii
import weakref
from . import signals
from .core import Widget, ContentWidget


class Button(ContentWidget):
    '''
    Push button widgets

    Attributes:
        _is_pushed (bool): Button state
    '''
    def __init__(self, label, parent, focus_key = None):
        # Initialize inherited state.
        super().__init__(label, parent, focus_key)

        # Initialize size.
        self.fit()

    def report(self):
        return {'usage': 'Enter:Execute'}


    def focus(self):
        # This button has yet to be pushed.
        self._is_pushed = False


    def compose(self):
        # Bubble a data signal if this button was pressed.
        return (self._is_pushed, {})


    def draw(self):
        width = self.get_size()[0]

        # Draw bounding parenthesis.
        self.draw_text('(', attr = self.style('text'))
        self.draw_text(')', margin = (width - 1, 0, 0, 0), attr = self.style('text'))

        # Draw button label within parenthesis.
        self.draw_text(self._label, padding = (1, 1), margin = (1, 1, 0, 0), align = 'CENTER', hint = self._focus_key, attr = self.style('text'))


    def operate(self, c):
        # Push this button.
        if c in {curses.KEY_ENTER, ascii.LF, ascii.CR}:
            self._is_pushed = True
            return 'END'

        return 'CONTINUE'


    def fit(self):
        ''' Fits button to padded label width '''
        self.resize(len(self._label) + 4, 1)


class SelectionList(ContentWidget):
    def __init__(self, label, parent, focus_key = None):
        # Initialize inherited state.
        super().__init__(label, parent, focus_key)

        # Initialize attributes.
        self.items = []
        self.highlight = 0
        self.selection = None

    def report(self):
        return {'usage': 'Up/Down:Scroll, Enter:Select'}

    def operate(self, c):
        if c in {curses.KEY_DOWN, curses.KEY_UP, curses.KEY_ENTER, ascii.LF, ascii.CR}:
            self.tag_redraw()

            # Highlight the next item, wrapping if necessary.
            if c == curses.KEY_DOWN:
                if self.highlight + 1 == len(self.items):
                    self.highlight = 0
                else:
                    self.highlight += 1

            # Highlight the previous item, wrapping if necessary.
            elif c == curses.KEY_UP:
                if self.highlight == 0:
                    self.highlight = len(self.items) - 1
                else:
                    self.highlight -= 1

            # Select the highlighted item.
            elif c in {curses.KEY_ENTER, ascii.LF, ascii.CR}:
                self.selection = self.highlight

        return 'CONTINUE'


    def draw(self):
        items = self.items

        # Add a border.
        self.draw_border()
        self.draw_text(self._label, row = 0, padding = (1, 1), margin = (1, 1, 0, 1), hint = self._focus_key, align = 'CENTER')

        # Draw the items of this list.
        for i in range(len(items)):
            item = items[i]

            # Draw the current item.
            if i == self.highlight:
                attr = self.style('highlight')
            else:
                attr = self.style('text')
            self.draw_text(item, row = i + 1, margin = (4, 1, 1, 1), attr = attr, expand = 'RIGHT')

            # Draw the selected item.
            if i == self.selection:
                self.draw_text('*', row = i + 1, margin = (2, 1, 1, 1), attr = attr)


class StatusLine(ContentWidget):
    '''
    Displays usage instructions, feedback messages, and confirmation prompts

    Attributes:
        _error (bool):
        _mode (str): Mode of operation in
            {'PROMPT_CONFIRM', 'DISPLAY_FEEDBACK'}
        _feedback (str): Message containing feedback
        _prompt (str): Confirmation prompt
        _sigconfirm (str): Name of confirmation signal to emit
        _status (str): Status report
    '''
    def __init__(self, label, parent, focus_key = None):
        # Initialize inherited state.
        super().__init__(label, parent, focus_key)

        # Setup signal handling.
        self.add_signal_handler('UI_FEEDBACK', self._display_feedback)
        self.add_signal_handler('UI_PROMPT_CONFIRM', self._prompt_confirm)
        self.add_signal_handler('UI_UPDATE_STATUS', self._update_status)

        # Initialize attributes.
        self._mode = ''
        self._error = ''
        self._feedback = ''
        self._prompt = ''
        self._sigconfirm = ''
        self._status = ''
        self._timer = 0


    def draw(self):
        text = ''
        post_text = ''
        spacer = 3
        margin = [1, 1, 1, 1]
        attr = self.style('status')
        width, height = self.get_size()

        # Format text according to focus state and mode of operation.
        if Widget.input_focus is self:
            if self._mode == 'PROMPT_CONFIRM':
                post_text = 'Enter:OK, Esc:Cancel'
                text = self._prompt
            elif self._mode == 'DISPLAY_FEEDBACK':
                text = ('ERROR' if self._error else 'SUCCESS') + ': ' + self._feedback
                post_text = 'Enter/Esc:Continue'
                attr = self.style('error') if self._error else self.style('success')
            margin[1] += len(post_text) + spacer
        else:
            text = self._status

        # Tag for redraw in order to animate the scroll.
        effective_width = width - margin[0] - margin[1]
        if len(text) > effective_width:
            self.tag_redraw()

        # Draw status line text content.
        self.draw_text(text, row = 1, margin = margin, fit = 'AUTO_SCROLL', attr = attr)
        margin = [width - len(post_text) - 1, 1, 1, 1]
        self.draw_text(post_text, row = 1, margin = margin, attr = attr)

        # Draw border around status line.
        self.draw_border(attr = attr)


    def operate(self, c):
        # Display prompt until user either confirms or cancels.
        if self._mode == 'PROMPT_CONFIRM':

            # Confirm.
            if c in {curses.KEY_ENTER, ascii.LF, ascii.CR}:

                # Emit the requested confirmation signal.
                signal = signals.Signal(self._sigconfirm)
                self.bubble(**signal.data)

                return 'END'

        # Display feedback message until user presses a key.
        elif self._mode == 'DISPLAY_FEEDBACK':
            if c in {curses.KEY_ENTER, ascii.LF, ascii.CR}:
                return 'END'

        return 'CONTINUE'


    def _display_feedback(self, message, error, **kwargs):
        '''
        Prompts the user for confirmation (OK, Cancel)

        Parameters:
            prompt (str): Confirmation request message
            sigconfirm (Signal): Signal to emit upon confirmation
        '''
        self._mode = 'DISPLAY_FEEDBACK'
        self._feedback = message
        self._error = error
        Widget.input_focus = self


    def _prompt_confirm(self, prompt, sigconfirm, **kwargs):
        '''
        Prompts the user for confirmation (OK, Cancel)

        Parameters:
            prompt (str): Confirmation request message
            sigconfirm (Signal): Signal to emit upon confirmation
        '''
        self._mode = 'PROMPT_CONFIRM'
        self._prompt = prompt
        self._sigconfirm = sigconfirm
        Widget.input_focus = self


    def _update_status(self, status, **kwargs):
        ''' Updates status line usage information '''
        self.update_timestamp()
        self._status = status
        self.tag_redraw()


class Tab(ContentWidget):
    '''
    Tabbed container for widgets

    Attributes:
        _tab_list (list<Tab>): List of sibling tabs
    '''
    def __init__(self, label, parent, focus_key = None):
        # Initialize inherited state.
        super().__init__(label, parent, focus_key)

        # Initialize attributes.
        self._tab_list = []

        # Update tab list.
        if parent:
            tab_list = [node for node in parent._children if type(node) is Tab]
        else:
            tab_list = [self]

        # Synchronize sibling tab lists.
        for tab in tab_list:
            tab._tab_list = tab_list

        # Only show the first tab of the list.
        tab_list[0].show()
        for tab in tab_list[1:]:
            tab.hide()


    def focus(self):
        # Hide all sibling tabs.
        for tab in self._tab_list:
            tab.hide()
        self.show()


    def draw(self):
        width, height = self.get_size()
        margin = [2, 1, 1, height - 3]
        margin_left = margin_right = 0

        # Draw sibling tabs.
        for tab in self._tab_list:

            # Determine dimensions of tab label.
            tab_width = len(tab.label) + 4
            margin[1] = width - margin[0] - tab_width

            # Draw border around sibling tab's label.
            if tab is self:
                margin_left = margin[0]
                margin_right = margin[1]
            else:
                self.draw_border(
                    offset_left = margin[0],
                    offset_right = margin[1],
                    offset_bottom = margin[3],
                    attr = self.style('inactive')
                )
            margin[0] += 2

            # Draw sibling tab's label.
            if tab is not self:
                self.draw_text(
                    tab.label, row = 1, margin = margin, hint = tab._focus_key,
                    attr = self.style('inactive')
                )
            margin[0] += tab_width

        # Add border around contained widgets.
        self.draw_border(offset_top = 2)

        # Draw border around this tab.
        margin[0] = margin_left
        margin[1] = margin_right
        self.draw_border(
            offset_left = margin[0],
            offset_right = margin[1],
            offset_bottom = margin[3],
            char_bottom = ord(' '),
            char_bottom_left = curses.ACS_LRCORNER,
            char_bottom_right = curses.ACS_LLCORNER
        )
        margin[0] += 2

        # Draw this tab's label.
        self.draw_text(
            self._label, row = 1, margin = margin, hint = self._focus_key,
            attr = self.style('label')
        )


class Text(ContentWidget):
    '''
    Text display widget

    Attributes
        _line_list (list<str>): Lines of text
    '''
    def __init__(self, label, parent, style = 'text'):
        '''
        Parameters:
            style (str): Theme style attribute for text content
        '''
        # Prevent this widget from receiving input focus.
        focus_key = None

        # Initialize inherited state.
        super().__init__(label, parent, focus_key)

        # Initialize attributes.
        self._style = style
        self._line_list = []


    def draw(self):
        # Draw all lines of text.
        line_list = self._line_list
        for i in range(len(line_list)):
            line = line_list[i]
            self.draw_text(line, row = i, attr = self.style(self._style))


    def add_line(self, line):
        '''
        Adds given line of text to this widget

        Parameters:
            line (str): Line of text
        '''
        self._line_list.append(line)


    def add_raw(self, raw):
        '''
        Adds given raw string, line-by-line, to this widget

        Parameters:
            raw (str): Raw string
        '''
        for line in raw.split('\n'):
            self.add_line(line)


class Label(ContentWidget):
    '''
    Widget that is used to display the label of another widget

    Attributes:
        _used_by (weakref<Widget>): Reference to widget that uses this label
        _text (str): Embellished text representation of the label
    '''
    @property
    def used_by(self):
        return self._used_by() if self._used_by else None


    def __init__(self, label, parent, used_by):
        # Prevent this widget from receiving input focus.
        focus_key = None

        # Initialize inherited state.
        super().__init__(label, parent, focus_key)

        # Initialize attributes.
        self._used_by = weakref.ref(used_by)
        self._text = used_by._label

        # Initialize size.
        self.fit()


    def embellish(self, prefix = '', suffix = ''):
        '''
        Embellishes the label with leading and trailing text

        Parameters:
            prefix (str): Text to add before label (Optional)
            suffix (str): Text to add after label (Optional)
        '''
        self._text = prefix + self.used_by._label + suffix
        self.fit()


    def draw(self):
        # Used referenced style.
        style = self.used_by.style

        # Draw the embellished label.
        self.draw_text(self._text, attr = style('label'), hint = self.used_by._focus_key)


    def fit(self):
        ''' Fits this widget's dimensions to its content '''
        self.resize(len(self._text), 1)


    def to_row(self, row):
        '''
        Aligns this label with the given row of the widget that uses it

        Parameters:
            row (int): Alignment row of widget that uses this label
        '''
        self.move(y = self.used_by.get_position()[1] + row)


    def to_leftside(self):
        ''' Moves this label to the left side of the widget that uses it '''
        x, y = self.used_by.get_position()
        self.move(x - len(self._text))


class Labeled(ContentWidget):
    '''
    Class of widgets where each displays its label in a separate sibling
    widget, allowing label to be displayed outside of this widget's bounds

    Attributes:
        _linked_label (weakref<Widget>): Widget to use for this widget's label
    '''
    @property
    def linked_label(self):
        ''' Getter for "linked_label" property '''
        return self._linked_label() if self._linked_label else None


    def __init__(self, label, parent, focus_key = None):
        # Initialize inherited state.
        super().__init__(label, parent, focus_key)

        # Insert label node into the tree of widgets.
        label = Label('label', parent, used_by = self)

        # Link this widget to the label.
        ref = weakref.ref(label)
        self._linked_label = ref
        self._links.append(ref)


class TextBox(Labeled):
    '''
    Multi-line text input widget
    '''
    def __init__(self, label, parent, focus_key = None):
        # Initialize inherited state.
        super().__init__(label, parent, focus_key)

        # Initialize attributes.
        self._text = ''


class InputField(Labeled):
    ''' General input widget '''
    def __init__(self, label, parent, focus_key = None):
        # Initialize inherited state.
        super().__init__(label, parent, focus_key)

        # Initialize size.
        self.resize(height = 3)

        # Embellish label.
        self.linked_label.embellish(suffix = ': ')


    def draw(self):
        # Position label to the left of the input field.
        self.linked_label.to_row(1)
        self.linked_label.to_leftside()

        # Draw border around the input field.
        self.draw_border()


class TextField(InputField):
    '''
    Text input widget

    Attributes:
        _text (str): Text input
        _is_obscured (bool): Flag controlling whether or not text is obscured
    '''
    def __init__(self, label, parent, focus_key = None):
        # Initialize inherited state.
        super().__init__(label, parent, focus_key)

        # Initialize attributes.
        self._text = ''
        self._is_obscured = False


    def report(self):
        return {'usage': 'Enter text input.'}


    def compose(self, **kwargs):
        return (True, {'text': self._text})


    def draw(self):
        # Draw the label and input field.
        super().draw()

        margin = [1, 1, 1, 1]

        #  Draw the text input.
        text = self._text
        text = '*' *  len(text) if self._is_obscured else text
        self.draw_text(text, row = 1, padding = (0, 1), margin = margin, fit = 'CLIP_LEFT')

        # Draw the cursor.
        margin[0] = min(len(text) + 1, self.get_size()[0] - 2)
        self.draw_text(' ', row = 1, margin = margin, attr = self.style('cursor'))


    def operate(self, c):
        # Add a character.
        if ascii.isprint(c):
            self.tag_redraw()
            self._text += chr(c)

        # Delete a character.
        elif c in {ascii.BS, ascii.DEL}:
            self.tag_redraw()
            self._text = self._text[:-1]

        return 'CONTINUE'


    def obscure(self):
        ''' Obscures text input behind asterisks '''
        self._is_obscured = True;


    def reveal(self):
        ''' Reveals text input '''
        self._is_obscured = False;


class NumericField(InputField):
    '''
    Integer input widget

    Attributes:
        _number (str): String representation of number
    '''
    def __init__(self, label, parent, focus_key = None):
        # Initialize inherited state.
        super().__init__(label, parent, focus_key)

        # Initialize attributes.
        self._number = ''

    def report(self):
        return {'usage': 'Enter numeric input.'}


    def compose(self, **kwargs):
        return (
            self._number != '',
            {'number': int(self._number) if self._number else None}
        )


    def draw(self):
        # Draw the label and input field.
        super().draw()

        margin = [1, 1, 1, 1]
        number = self._number

        #  Draw the numeric input.
        self.draw_text(number, row = 1, padding = (0, 1), margin = margin, fit = 'CLIP_LEFT')

        # Draw the cursor.
        margin[0] = min(len(number) + 1, self.get_size()[0] - 2)
        self.draw_text(' ', row = 1, margin = margin, attr = self.style('cursor'))


    def operate(self, c):
        # Add a digit.
        if ascii.isdigit(c):
            self.tag_redraw()
            self._number += chr(c)

        # Delete a character.
        elif c in {ascii.BS, ascii.DEL}:
            self.tag_redraw()
            self._number = self._number[:-1]

        return 'CONTINUE'


class SelectField(InputField):
    '''
    Enumerated input widget

    Attributes:
        _options (list<str>): Enumerated input options
        _options_limit (int): Maximum number of options to display
        _highlight (int): Highlighted index in list of options
        _init_highlight (int): Highlight index at the time of gaining focus
        _vert_scroll (int): Index corresponding to top of viewable region
        _expanded (bool): Flag indicating if options list is expanded/collapsed
        _overlayed (bool): Flag indicating if expanded options list has been
            drawn over siblings
        _auto_expand (bool): Flag controlling automated expansion of options
    '''
    def __init__(self, label, parent, focus_key = None):
        # Initialize inherited state.
        super().__init__(label, parent, focus_key)

        # Initialize attributes.
        self._options = ['-- NO SELECTION --']
        self._options_limit = -1
        self._highlight = 0
        self._init_highlight = 0
        self._vert_scroll = 0
        self._auto_expand = False
        self.collapse()


    def report(self):
        return {'usage': 'Up/Down:Scroll, Enter:Select'}


    def compose(self):
        highlight = self._highlight
        option = self._options[highlight]
        selection_changed = highlight != self._init_highlight
        return (selection_changed, {'option': option if highlight > 0 else None})


    def decompose(self, options, **kwargs):
        # Load options and update draw state.
        self.load_options(options)
        if self._expanded:
            self.expand()


    def focus(self):
        # Store initial highlighted option.
        self._init_highlight = self._highlight

        # Expand options list on focus if automated.
        if self._auto_expand:
            self.expand()

        # Scroll to the highlighted option.
        self._vert_scroll = self._highlight


    def blur(self):
        # Scroll to the highlighted option.
        self._vert_scroll = self._highlight

        # Collapse options list on blur if automated.
        if self._auto_expand:
            self.collapse()


    def draw(self):
        # Draw the label and input field.
        super().draw()

        width, height = self.get_size()
        margin = [1, 1, 1, 1]
        padding = (1, 1)

        # Draw the list of options.
        vert_scroll = self._vert_scroll
        options_section = self._options[vert_scroll:][:height - 2]
        for i in range(len(options_section)):
            option = options_section[i]

            # Format and style option.
            expand = 'AROUND' if not i + vert_scroll else 'RIGHT'
            if i + vert_scroll == self._highlight:
                attr = self.style('highlight')
            else:
                attr = self.style('text')

            # Draw option.
            self.draw_text(option, row = margin[2] + i, margin = margin, padding = padding, expand = expand, attr = attr)


    def operate(self, c):
        # Draw expanded options list over siblings.
        if self._expanded and not self._overlayed:
            self.tag_redraw()
            self._overlayed = True

        if c in {curses.KEY_DOWN, curses.KEY_UP, curses.KEY_ENTER, ascii.LF, ascii.CR}:
            self.tag_redraw()

            # Highlight the next option, wrapping if necessary.
            if c == curses.KEY_DOWN:
                self._highlight += 1
                self._highlight %= len(self._options)


            # Highlight the previous option, wrapping if necessary.
            elif c == curses.KEY_UP:
                self._highlight -= 1
                self._highlight %= len(self._options)

            # Select the highlighted option.
            elif c in {curses.KEY_ENTER, ascii.LF, ascii.CR}:
                return 'END'

            # Scroll list if necessary.
            effective_height = self.get_size()[1] - 2
            if self._highlight < self._vert_scroll:
                self._vert_scroll = self._highlight
            elif self._highlight >= self._vert_scroll + effective_height:
                self._vert_scroll = self._highlight - effective_height + 1

        return 'CONTINUE'

    def auto_expand(self):
        ''' Flags this widget for automated expansions of options list '''
        self._auto_expand = True


    def collapse(self):
        ''' Collapses the options list to display only a single option '''
        # Collapse options list.
        self.resize(height = 3)

        # Redraw siblings that may have been occluded by drop-down list.
        self._ancestor.tag_redraw()

        # Set state.
        self._expanded = False
        self._overlayed = False


    def expand(self):
        ''' Expands the options list to display multiple options '''
        # Expand options list.
        ph = self._parent.get_size()[1]
        sy = self.get_position()[1]
        option_count = ph if self._options_limit < 0 else self._options_limit
        option_count = min(option_count, ph - sy - 3)
        option_count = min(option_count, len(self._options))
        sh = option_count + 2
        self.resize(height = sh)

        # Set state.
        self._expanded = True


    def limit_options(self, count):
        '''
        Limits the number of options presented

        Parameters:
            count (int): Maximum number of options to display
        '''
        self._options_limit = max(1, count)
        if self._expanded:
            self.expand()


    def load_options(self, options):
        '''
        Loads enumerated options from a list

        Parameters:
            options (list<str>): Options list
        '''
        self._options = ['-- NO SELECTION --']
        self._options.extend(options)
