import curses
from typing import Dict, List, Tuple, Optional

class UserInterface:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.header_height = 1
        self.status_height = 2
        self.help_height = 1
        self.min_width = 80
        self.min_height = 15
        self.debug_mode = False
        self.compact_mode = False
        self.graph_height = 4   # Height of each resource graph
        self.graph_width = 60   # Width of resource graphs
        self.min_graph_height = 3  # Minimum height for graphs
        self.min_graph_width = 20  # Minimum width for graphs

    def check_terminal_size(self) -> Tuple[bool, str, bool]:
        """Check if terminal size is adequate and determine display mode"""
        height, width = self.stdscr.getmaxyx()
        debug_msg = f"Terminal size: {width}x{height}"
        
        if width < self.min_width or height < self.min_height:
            return False, f"Terminal too small. Minimum size required: {self.min_width}x{self.min_height}", False
        
        is_compact = height < 24 or width < 80  # Reduced thresholds for compact mode
        return True, debug_msg, is_compact

    def safe_addstr(self, y: int, x: int, text: str, attr: int = 0) -> bool:
        """Safely add string to screen, handling boundary conditions"""
        try:
            height, width = self.stdscr.getmaxyx()
            if 0 <= y < height and 0 <= x < width:
                # Truncate string if it would exceed screen width
                max_length = width - x
                if max_length > 0:
                    self.stdscr.addstr(y, x, text[:max_length], attr)
                    return True
        except curses.error:
            pass
        return False

    def draw_resource_graphs(self, resource_history, start_y: int) -> int:
        """Draw CPU and Memory usage graphs with fallback displays"""
        try:
            height, width = self.stdscr.getmaxyx()
            
            # Adjust graph dimensions based on terminal size
            available_width = width - 8  # Leave margin for labels
            available_height = height - start_y - self.status_height - self.help_height
            
            # Calculate actual graph dimensions with improved spacing
            actual_width = max(self.min_graph_width, min(self.graph_width, available_width - 2))
            actual_height = max(self.min_graph_height, min(self.graph_height, (available_height - 3) // 2))  # Extra space between graphs
            
            # Skip drawing graphs if terminal is too small
            if available_width < self.min_graph_width or available_height < (self.min_graph_height * 2 + 2):
                self.safe_addstr(start_y, 2, "Terminal too small for graphs", curses.color_pair(3))
                return start_y + 1
            
            try:
                # Draw CPU graph
                cpu_graph = resource_history.get_cpu_graph(actual_width, actual_height)
                for i, line in enumerate(cpu_graph):
                    self.safe_addstr(start_y + i, 2, line, curses.color_pair(1))
                
                # Draw Memory graph below CPU graph
                start_y += actual_height
                mem_graph = resource_history.get_memory_graph(actual_width, actual_height)
                for i, line in enumerate(mem_graph):
                    self.safe_addstr(start_y + i, 2, line, curses.color_pair(1))
                
                return start_y + actual_height + 1
                
            except Exception as e:
                # Fallback display if graph generation fails
                self.safe_addstr(start_y, 2, "Error drawing resource graphs", curses.color_pair(4))
                return start_y + 1
                
        except curses.error:
            return start_y

    def draw_header(self, width: int):
        """Draw application header"""
        header = "Process Monitor"
        self.safe_addstr(0, (width - len(header)) // 2, header, curses.color_pair(3) | curses.A_BOLD)

    def draw_process_list(self, processes: List[Dict], selected_idx: int, max_height: int, tree_view: bool):
        """Draw process list with tree view support"""
        if not processes:
            self.safe_addstr(self.header_height + 1, 2, "No processes found (0 processes)", curses.color_pair(3))
            return

        # Debug output for process count
        process_count = len(processes)
        self.safe_addstr(self.header_height, 2, f"Total processes: {process_count}", curses.color_pair(2) | curses.A_BOLD)

        # Fixed starting position after graphs
        start_y = self.header_height + (self.graph_height * 2) + 2  # Consistent spacing after graphs

        # Debug output for start_y position
        if self.debug_mode:
            self.safe_addstr(0, 0, f"Debug: start_y={start_y}, max_height={max_height}", curses.color_pair(1))

        list_height = max_height - start_y - self.status_height - self.help_height
            
        tree_prefix = "  " if not tree_view else "├─ "
        
        # Calculate visible window for processes
        window_start = max(0, min(selected_idx - list_height // 2, len(processes) - list_height))
        visible_processes = processes[window_start:window_start + list_height]

        # Draw process list border
        height, width = self.stdscr.getmaxyx()
        list_width = width - 4  # Leave 2 chars padding on each side
        
        # Draw top border
        self.safe_addstr(start_y, 1, "┌" + "─" * (list_width - 2) + "┐", curses.color_pair(1))
        
        # Draw column headers
        headers = f"{'PID':>8} {'CPU%':>7} {'MEM%':>7} {'STATUS':>10} {'NAME':<20}"
        self.safe_addstr(start_y + 1, 2, headers, curses.color_pair(1) | curses.A_BOLD)
        
        # Draw header separator
        self.safe_addstr(start_y + 2, 1, "├" + "─" * (list_width - 2) + "┤", curses.color_pair(1))

        # Adjust start_y for content
        start_y += 3

        # Draw processes with enhanced visual style
        for idx, proc in enumerate(visible_processes):
            if start_y + idx + 1 >= max_height - 2:  # Leave space for status and help
                break

            try:
                indent = "  " * proc.get('level', 0) if tree_view else ""
                prefix = tree_prefix if proc.get('level', 0) > 0 else ""
                name_str = f"{indent}{prefix}{proc['name']}"
                
                # Format process information with proper spacing
                line = f"{proc['pid']:>8} {proc['cpu_percent']:>7.1f} {proc['memory_percent']:>7.1f} "
                line += f"{proc['status']:>10} {name_str:<40}"

                # Enhanced color scheme for better visibility
                if idx + window_start == selected_idx:
                    attr = curses.color_pair(3) | curses.A_REVERSE
                else:
                    attr = curses.color_pair(2)
                    if proc['cpu_percent'] > 50 or proc['memory_percent'] > 50:
                        attr |= curses.A_BOLD

                # Draw side borders
                self.safe_addstr(start_y + idx, 1, "│", curses.color_pair(1))
                self.safe_addstr(start_y + idx, width - 2, "│", curses.color_pair(1))
                # Draw process info
                self.safe_addstr(start_y + idx, 2, line, attr)
            except (KeyError, ValueError):
                # Handle missing or invalid process data
                self.safe_addstr(start_y + idx, 2, "Error: Unable to display process info", curses.color_pair(4))
            
        # Draw bottom border
        self.safe_addstr(start_y + len(visible_processes), 1, "└" + "─" * (list_width - 2) + "┘", curses.color_pair(1))

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
        help_text = "q:Quit | ↑/↓:Navigate | s:Sort | /:Search | f:Filter | c:Clear | t:Tree | Enter:Details | x:Terminate"
        self.safe_addstr(max_y - 1, 0, f"{help_text:<{width}}", curses.color_pair(2))
        
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