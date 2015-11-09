#!/bin/env python3


from mock_dbmanager import DatabaseManager
from ui import build_ui
from uiframework import signals


def main():
    # Initialize database manager (model), UI (view), and signal router (hub).
    signal_router = signals.SignalRouter()
    dbm = DatabaseManager(signal_router)
    ui = build_ui(signal_router)

    # Run the application.
    ui.run()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import curses
        curses.endwin()
        raise e
