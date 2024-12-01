#!/usr/bin/env python3
import curses
import sys
from process_manager import ProcessManager
from ui_components import UserInterface
from keybindings import handle_input

def main(stdscr):
    # Initialize curses
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)
    stdscr.timeout(1000)  # Set input timeout for updates

    # Initialize color pairs
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_RED, -1)

    # Initialize components
    process_manager = ProcessManager()
    ui = UserInterface(stdscr)
    search_term = ""
    selected_idx = 0
    sort_by = "cpu"
    running = True

    while running:
        # Get terminal dimensions
        max_y, max_x = stdscr.getmaxyx()

        # Update process list
        processes = process_manager.get_processes(sort_by)
        if search_term:
            processes = process_manager.filter_processes(processes, search_term)

        # Draw UI
        ui.draw_header(max_x)
        ui.draw_process_list(processes, selected_idx, max_y - 3)
        ui.draw_status_bar(max_x, sort_by, search_term)
        ui.draw_help(max_x)

        # Handle input
        key = stdscr.getch()
        if key != -1:
            result = handle_input(key, selected_idx, len(processes), search_term, sort_by)
            if result is None:
                running = False
            else:
                selected_idx, search_term, sort_by = result

        stdscr.refresh()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
