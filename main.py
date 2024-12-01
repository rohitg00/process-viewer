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
    last_size = stdscr.getmaxyx()

    while running:
        # Check terminal size
        size_ok, error_msg = ui.check_terminal_size()
        if not size_ok:
            stdscr.clear()
            ui.draw_error(error_msg)
            stdscr.refresh()
            key = stdscr.getch()
            if key in (ord('q'), ord('Q')):
                running = False
            continue

        # Handle window resize
        current_size = stdscr.getmaxyx()
        if current_size != last_size:
            stdscr.clear()
            curses.resize_term(*current_size)
            last_size = current_size

        try:
            # Get terminal dimensions
            max_y, max_x = stdscr.getmaxyx()

            # Update process list
            processes = process_manager.get_processes(sort_by)
            if search_term:
                processes = process_manager.filter_processes(processes, search_term)

            # Ensure selected index is within bounds
            if processes:
                selected_idx = max(0, min(selected_idx, len(processes) - 1))

            # Draw UI with error handling
            try:
                stdscr.clear()
                # Verify terminal size before drawing
                if max_y < ui.min_height or max_x < ui.min_width:
                    raise curses.error(f"Terminal too small. Min size: {ui.min_width}x{ui.min_height}")
                
                ui.draw_header(max_x)
                ui.draw_process_list(processes, selected_idx, max_y)
                ui.draw_status_bar(max_x, sort_by, search_term)
                ui.draw_help(max_x)
            except curses.error as e:
                stdscr.clear()
                ui.draw_error(f"Display error: {str(e)}")
                stdscr.refresh()
                continue

            # Handle input
            key = stdscr.getch()
            if key != -1:
                if key == curses.KEY_RESIZE:
                    continue

                result = handle_input(key, selected_idx, len(processes), search_term, sort_by)
                if result is None:
                    running = False
                else:
                    selected_idx, search_term, sort_by = result

            stdscr.refresh()

        except curses.error as e:
            stdscr.clear()
            ui.draw_error(f"Display error: {str(e)}")
            stdscr.refresh()
            continue

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)
