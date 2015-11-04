# Filename: signals.py
# Creation Date: Thu 08 Oct 2015
# Last Modified: Thu 03 Nov 2015 09:40:15 PM MDT
# Author: Brett Fedack


import inspect
import weakref


class Signal():
    '''
    Data carrying signal class

    Attributes:
        _name (str): Signal identifier
        _data (dict): Data carried by a signal; expanded to handler arguments
        _propagate (bool): Flag controlling whether or not a signal can be
            handled multiple times
        _is_alive (bool): Flag controlling whether or not a signal can be
            handled
    '''
    def __init__(self, name, data = dict(), propagate = True):
        '''
        Parameters:
            name (str): _name attribute initializer
            data (dict): _data attribute initializer (Optional)
            propagate (bool): _propagate attribute initializer (Optional)
        '''
        self._name = name
        self._data = data
        self._propagate = propagate
        self._is_alive = True


    @property
    def name(self):
        ''' Getter for "_name" attribute '''
        return self._name


    @name.setter
    def name(self, value):
        raise AttributeError('This attribute is read-only')


    @property
    def data(self):
        ''' Getter for "_data" attribute '''
        return self._data


    @data.setter
    def data(self, value):
        raise AttributeError('This attribute cannot be reassigned')


    @property
    def propagate(self):
        ''' Getter for "_propagate" attribute '''
        return self._propagate


    @propagate.setter
    def propagate(self, value):
        raise AttributeError('This attribute is read-only')


    @property
    def is_alive(self):
        ''' Getter for "_is_alive" attribute '''
        return self._is_alive


    @is_alive.setter
    def is_alive(self, value):
        raise AttributeError('This attribute is read-only')


    def kill(self):
        ''' Prevents this signal from being handled '''
        self._is_alive = False


class SignalRouter():
    '''
    Mediator for managing signal handlers and forwarding received signals

    Attributes:
        _signal_handlers (dict): Signal handler lists keyed by signal name
    '''
    def __init__(self):
        self._signal_handlers = dict()


    def forward(self, signal, reverse = False):
        '''
        Forwards the given signal to registered signal handlers

        Parameters:
            signal (Signal): Received signal to forward
            reverse (bool): Flag controlling order of signal handler traversal
                (Optional)

        Returns:
            bool: True if given signal is forwarded; false otherwise
        '''
        # Determine if the signal can be handled.
        if signal.is_alive and signal.name in self._signal_handlers:

            # Create a shallow working copy of the signal handlers list.
            handlers_list = self._signal_handlers[signal.name].copy()
            if reverse:
                handlers_list.reverse()

            # Preemptively kill a signal that is not allowed to propagate.
            if not signal.propagate:
                signal.kill()
                handlers_list = handlers_list[:1]

            # Visit registered signal handlers in order.
            for handler in handlers_list:

                # Handle the signal.
                handler()(**signal.data) # Called from weak reference


    def register(self, signame, handler):
        '''
        Registers the given signal handler for signal forwarding

        Parameters:
            signame (str): Signal name
            handler (function): Signal handler
        '''
        # Create a weak reference to the function/method handler.
        if inspect.ismethod(handler):
            handler = weakref.WeakMethod(handler)
        elif inspect.isfunction(handler):
            handler = weakref.ref(handler)
        else:
            return

        # Add given non-duplicate handler to respective signal handlers list.
        if signame in self._signal_handlers:
            if handler not in self._signal_handlers[signame]:
                self._signal_handlers[signame].append(handler)
        else:
            self._signal_handlers[signame] = [handler]


    def deregister(self, signame, handler):
        '''
        Deregisters given signal handler

        Parameters:
            signame (str): Signal name
            handler (function): Signal handler
        '''
        # Compare function/method handlers by weak reference.
        if inspect.ismethod(handler):
            handler = weakref.WeakMethod(handler)
        elif inspect.isfunction(handler):
            handler = weakref.ref(handler)
        else:
            return

        # Remove given handler from respective signal handlers list.
        if (signame in self._signal_handlers
            and handler in self._signal_handlers[signame]
        ):
            self._signal_handlers[signame].remove(handler)

            # Remove signal name if it is associated with an empty list.
            if not self._signal_handlers[signame]:
                del self._signal_handlers[signame]


    def print(self):
        ''' Prints the contents of this signal router for debugging '''
        print()
        for signame in self._signal_handlers:
            print('signame: {}'.format(signame))
            handlers_list = self._signal_handlers[signame]
            for handler in handlers_list:
                print('    handler: {}'.format(handler()))
