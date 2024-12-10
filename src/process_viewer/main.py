#!/usr/bin/env python3
"""
Process Viewer - A terminal-based system process monitoring tool

This is the main entry point for the Process Viewer application. It handles the
initialization of the curses interface, manages the application state, and
coordinates the interaction between different components.

The application provides real-time monitoring of system processes with features like:
- Process list with CPU/Memory usage
- Resource usage graphs
- Process tree view
- Interactive filtering and sorting
- Process management capabilities
"""

import curses
import sys
from process_viewer.process_manager import ProcessManager
from process_viewer.ui_components import UserInterface
from process_viewer.keybindings import handle_input
from process_viewer.resource_graphs import ResourceHistory

def main(stdscr):
    """
    Main application loop handling the curses interface and application state

    Args:
        stdscr: The main curses window object

    The function initializes the curses interface, sets up the color scheme,
    manages the application state, and handles the main event loop for user
    interaction and display updates.
    """
    # Initialize curses interface and configure settings
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)
    stdscr.timeout(1000)  # Set input timeout for updates

    # Initialize color pairs for enhanced purple theme
    curses.init_pair(1, 92, -1)      # Light purple for borders
    curses.init_pair(2, 99, -1)      # Bright purple for process list
    curses.init_pair(3, 141, -1)     # Vivid purple for highlights
    curses.init_pair(4, 97, -1)      # Medium purple for graphs
    
    # Try to set background color if supported
    try:
        curses.init_pair(5, curses.COLOR_WHITE, 54)  # White text on dark purple background
        curses.init_pair(6, 213, 54)  # Light purple on dark purple
    except curses.error:
        pass

    # Initialize components
    process_manager = ProcessManager()
    ui = UserInterface(stdscr)
    resource_history = ResourceHistory()
    state = {
        'selected_idx': 0,
        'search_term': "",
        'sort_by': "cpu",
        'input_mode': "normal",
        'tree_view': True,
        'filters': {
            'status': None,
            'min_cpu': None,
            'min_memory': None,
            'user_filter': None
        },
        'process_count': 0,
        'process_manager': process_manager,
        'processes': [],
        'status_message': ""
    }
    running = True
    last_size = stdscr.getmaxyx()

    while running:
        # Check terminal size
        size_ok, debug_msg, is_compact = ui.check_terminal_size()
        if not size_ok:
            stdscr.clear()
            ui.draw_error(debug_msg)
            stdscr.refresh()
            key = stdscr.getch()
            if key in (ord('q'), ord('Q')):
                running = False
            continue
        
        # Show debug information if enabled
        if ui.debug_mode:
            stdscr.addstr(0, 0, debug_msg, curses.color_pair(1))
            stdscr.refresh()

        # Handle window resize
        current_size = stdscr.getmaxyx()
        if current_size != last_size:
            stdscr.clear()
            curses.resize_term(*current_size)
            last_size = current_size

        try:
            # Get terminal dimensions
            max_y, max_x = stdscr.getmaxyx()

            # Update process list with error handling
            try:
                processes = process_manager.get_processes(state['sort_by'], state['tree_view'])
                if ui.debug_mode:
                    print(f"Debug: Retrieved {len(processes)} processes before filtering")
                
                processes = process_manager.filter_processes(
                    processes,
                    search_term=state['search_term'],
                    status=state['filters']['status'],
                    min_cpu=state['filters']['min_cpu'],
                    min_memory=state['filters']['min_memory'],
                    user_filter=state['filters']['user_filter']
                )
                
                state['processes'] = processes
                state['process_count'] = len(processes)
                
                if ui.debug_mode:
                    print(f"Debug: {state['process_count']} processes after filtering")

                # Handle empty process list
                if not processes:
                    state['status_message'] = "No processes found matching criteria"
                    state['selected_idx'] = 0
                else:
                    # Ensure selected index is within bounds
                    state['selected_idx'] = max(0, min(state['selected_idx'], len(processes) - 1))
            except Exception as e:
                state['status_message'] = f"Error updating process list: {str(e)}"
                state['processes'] = []
                state['process_count'] = 0
                state['selected_idx'] = 0

            # Draw UI with error handling
            try:
                stdscr.clear()
                # Verify terminal size before drawing
                if max_y < ui.min_height or max_x < ui.min_width:
                    raise curses.error(f"Terminal too small. Min size: {ui.min_width}x{ui.min_height}")
                
                ui.draw_header(max_x)
                
                # Update and draw resource graphs with error handling
                try:
                    update_success = resource_history.update()
                    if not update_success:
                        ui.safe_addstr(ui.header_height + 1, 2, "Failed to update system resources", curses.color_pair(4))
                        start_y = ui.header_height + 2
                    else:
                        start_y = ui.draw_resource_graphs(resource_history, ui.header_height + 1)
                except Exception as e:
                    ui.safe_addstr(ui.header_height + 1, 2, f"Resource monitoring error: {str(e)}", curses.color_pair(4))
                    start_y = ui.header_height + 2

                # Optimize vertical space allocation with debug output
                min_process_list_height = 5  # Increased minimum height
                remaining_height = max_y - start_y - ui.status_height - ui.help_height
                
                if ui.debug_mode:
                    print(f"Debug: max_y={max_y}, start_y={start_y}, remaining_height={remaining_height}")
                    print(f"Debug: Process count before display: {len(processes)}")
                
                # Ensure minimum space for process list
                if remaining_height < min_process_list_height:
                    ui.graph_height = max(3, ui.graph_height - (min_process_list_height - remaining_height))
                    start_y = ui.header_height + (ui.graph_height * 2) + 2  # Recalculate start_y with spacing
                    remaining_height = max_y - start_y - ui.status_height - ui.help_height
                    
                    if ui.debug_mode:
                        print(f"Debug: Adjusted graph_height={ui.graph_height}, new remaining_height={remaining_height}")
                
                ui.draw_process_list(processes, state['selected_idx'], remaining_height, state['tree_view'])
                ui.draw_status_bar(max_x, state)
                ui.draw_help(max_x)
                
                # Draw filter menu if in filter menu mode
                if state['input_mode'] == 'filter_menu':
                    ui.draw_filter_menu()
                
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

                new_state = handle_input(key, state)
                if new_state is None:
                    running = False
                else:
                    state = new_state

            stdscr.refresh()

        except curses.error as e:
            stdscr.clear()
            ui.draw_error(f"Display error: {str(e)}")
            stdscr.refresh()
            continue

def run():
    """Entry point for the process viewer application"""
    return curses.wrapper(main)

if __name__ == "__main__":
    try:
        sys.exit(run())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)
