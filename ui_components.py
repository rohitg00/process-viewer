import curses
from typing import Tuple

class UserInterface:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.header_height = 2
        self.status_height = 1
        self.help_height = 1
        self.min_width = 80
        self.min_height = 15
        self.debug_mode = False
        self.compact_mode = False

    def check_terminal_size(self) -> Tuple[bool, str, bool]:
        """Check if terminal size is adequate and determine display mode"""
        height, width = self.stdscr.getmaxyx()
        debug_info = f"Terminal size: {width}x{height}"
        
        if height < 10 or width < 40:  # Absolute minimum requirements
            return False, f"Terminal too small. Minimum size: 40x10, Current: {width}x{height}", False
            
        if height < self.min_height or width < self.min_width:
            self.compact_mode = True
            return True, f"Running in compact mode. {debug_info}", True
            
        self.compact_mode = False
        return True, debug_info, False

    def safe_addstr(self, y: int, x: int, text: str, attr=0):
        """Safely add string to screen with bounds checking"""
        height, width = self.stdscr.getmaxyx()
        if y < 0 or y >= height:
            return
        if x < 0:
            return
        
        # Truncate string if it would exceed screen width
        max_length = width - x
        if max_length <= 0:
            return
            
        try:
            if len(text) > max_length:
                text = text[:max_length-3] + "..."
            self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass

    def draw_header(self, width):
        try:
            header = "Process Viewer"
            # Make sure width is within bounds
            if width <= 0:
                return
            
            # Draw header border and title
            self.safe_addstr(0, 0, "═" * min(width, self.stdscr.getmaxyx()[1]), curses.color_pair(1))
            self.safe_addstr(1, 2, f"{header:^{width-4}}", curses.color_pair(2) | curses.A_BOLD)
            self.safe_addstr(2, 0, "═" * min(width, self.stdscr.getmaxyx()[1]), curses.color_pair(1))
        except curses.error:
            return

    def draw_process_list(self, processes, selected_idx, max_rows):
        if self.compact_mode:
            start_y = 1  # Reduce header space in compact mode
            list_height = max_rows - 3  # Leave minimal space for status and help
        else:
            start_y = self.header_height + 1
            list_height = max_rows - self.header_height - self.status_height - self.help_height - 2
        
        # Calculate visible window for processes
        window_start = max(0, min(selected_idx - list_height // 2, len(processes) - list_height))
        visible_processes = processes[window_start:window_start + list_height]

        # Draw column headers
        headers = f"{'PID':>8} {'CPU%':>7} {'MEM%':>7} {'STATUS':>10} {'NAME':<20}"
        self.safe_addstr(start_y, 2, headers, curses.color_pair(1) | curses.A_BOLD)

        # Draw processes
        for idx, proc in enumerate(visible_processes):
            if start_y + idx + 1 >= max_rows - 2:  # Leave space for status and help
                break

            try:
                line = f"{proc['pid']:>8} {proc['cpu_percent']:>7.1f} {proc['memory_percent']:>7.1f} "
                line += f"{proc['status']:>10} {proc['name']:<20}"

                attr = curses.color_pair(3) | curses.A_REVERSE if idx + window_start == selected_idx else curses.color_pair(1)
                self.safe_addstr(start_y + idx + 1, 2, line, attr)
            except (KeyError, ValueError):
                # Handle missing or invalid process data
                self.safe_addstr(start_y + idx + 1, 2, "Error: Unable to display process info", curses.color_pair(4))

    def draw_status_bar(self, width, state):
        max_y = self.stdscr.getmaxyx()[0]
        sort_by = state['sort_by']
        search_term = state['search_term']
        filters = state['filters']
        input_mode = state['input_mode']
        
        # Build status text
        status = f"Sort: {sort_by.upper()}"
        if search_term:
            status += f" | Search: {search_term}"
        
        # Add active filters
        active_filters = []
        if filters['status']:
            active_filters.append(f"Status: {filters['status']}")
        if filters['min_cpu'] is not None:
            active_filters.append(f"CPU>={filters['min_cpu']}%")
        if filters['min_memory'] is not None:
            active_filters.append(f"Mem>={filters['min_memory']}%")
        if filters['user_filter']:
            active_filters.append(f"User: {filters['user_filter']}")
        
        if active_filters:
            status += " | Filters: " + ", ".join(active_filters)
            
        # Show current input mode
        if input_mode != 'normal':
            mode_text = {
                'search': 'SEARCH',
                'filter_menu': 'FILTER MENU',
                'filter_1': 'ENTER STATUS (r/s/t/z)',
                'filter_2': 'ENTER CPU THRESHOLD',
                'filter_3': 'ENTER MEMORY THRESHOLD',
                'filter_4': 'ENTER USERNAME'
            }.get(input_mode, input_mode.upper())
            status += f" | Mode: {mode_text}"
            
        self.safe_addstr(max_y - 2, 0, f"{status:<{width}}", curses.color_pair(2) | curses.A_BOLD)

    def draw_help(self, width):
        max_y = self.stdscr.getmaxyx()[0]
        help_text = "q:Quit | ↑/↓:Navigate | s:Sort | /:Search | f:Filter | c:Clear | Enter:Details | x:Terminate"
        self.safe_addstr(max_y - 1, 0, f"{help_text:<{width}}", curses.color_pair(1))
        
    def draw_filter_menu(self):
        """Draw the filter menu when in filter_menu mode"""
        height, width = self.stdscr.getmaxyx()
        menu_height = 6
        menu_width = 40
        start_y = (height - menu_height) // 2
        start_x = (width - menu_width) // 2
        
        menu_items = [
            "Filter Menu",
            "1. Filter by Status (running/sleeping/...)",
            "2. Filter by CPU Usage",
            "3. Filter by Memory Usage",
            "4. Filter by Username",
            "ESC to cancel, c to clear all filters"
        ]
        
        for i, item in enumerate(menu_items):
            if i == 0:
                self.safe_addstr(start_y + i, start_x, item.center(menu_width), curses.color_pair(2) | curses.A_BOLD)
            else:
                self.safe_addstr(start_y + i, start_x, item.ljust(menu_width), curses.color_pair(1))

    def draw_error(self, message: str):
        """Draw an error message in the center of the screen"""
        try:
            height, width = self.stdscr.getmaxyx()
            y = height // 2
            x = max(0, (width - len(message)) // 2)
            self.stdscr.clear()
            self.safe_addstr(y, x, message, curses.color_pair(4) | curses.A_BOLD)
        except curses.error:
            pass

    def draw_process_details(self, process_details, width):
        """Draw detailed process information"""
        if not process_details:
            self.draw_error("Process not found or access denied")
            return

        height, _ = self.stdscr.getmaxyx()
        start_y = height // 4
        start_x = width // 6
        box_width = int(width * 2/3)

        # Draw border
        for y in range(start_y, start_y + 10):
            self.safe_addstr(y, start_x, "│", curses.color_pair(1))
            self.safe_addstr(y, start_x + box_width, "│", curses.color_pair(1))
        
        self.safe_addstr(start_y, start_x, "┌" + "─" * (box_width - 2) + "┐", curses.color_pair(1))
        self.safe_addstr(start_y + 9, start_x, "└" + "─" * (box_width - 2) + "┘", curses.color_pair(1))

        # Draw title
        title = f" Process Details: {process_details['name']} (PID: {process_details['pid']}) "
        self.safe_addstr(start_y, start_x + (box_width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)

        # Draw details
        details = [
            f"Status: {process_details['status']}",
            f"CPU Usage: {process_details['cpu_percent']:.1f}%",
            f"Memory Usage: {process_details['memory_percent']:.1f}%",
            f"Created: {process_details['create_time']}",
            f"User: {process_details['username']}",
            f"Command: {process_details['cmdline'][:box_width-20]}"
        ]

        for i, detail in enumerate(details, 1):
            self.safe_addstr(start_y + i + 1, start_x + 2, detail, curses.color_pair(1))

        # Draw exit message
        self.safe_addstr(start_y + 8, start_x + 2, "Press 'q' or ESC to return", curses.color_pair(3))

    def draw_confirmation_dialog(self, pid):
        """Draw a confirmation dialog for process termination"""
        height, width = self.stdscr.getmaxyx()
        dialog_height = 5
        dialog_width = 40
        start_y = (height - dialog_height) // 2
        start_x = (width - dialog_width) // 2

        # Draw border
        for y in range(start_y, start_y + dialog_height):
            self.safe_addstr(y, start_x, "│", curses.color_pair(4))
            self.safe_addstr(y, start_x + dialog_width, "│", curses.color_pair(4))
        
        self.safe_addstr(start_y, start_x, "┌" + "─" * (dialog_width - 2) + "┐", curses.color_pair(4))
        self.safe_addstr(start_y + dialog_height - 1, start_x, "└" + "─" * (dialog_width - 2) + "┘", curses.color_pair(4))

        # Draw message
        message = f"Terminate process {pid}?"
        self.safe_addstr(start_y + 1, start_x + (dialog_width - len(message)) // 2, message, curses.color_pair(4) | curses.A_BOLD)
        confirm_text = "Press 'y' to confirm, 'n' to cancel"
        self.safe_addstr(start_y + 3, start_x + (dialog_width - len(confirm_text)) // 2, confirm_text, curses.color_pair(1))