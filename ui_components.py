import curses
from typing import Tuple

class UserInterface:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.header_height = 2
        self.status_height = 1
        self.help_height = 1
        self.min_width = 80
        self.min_height = 20

    def check_terminal_size(self) -> Tuple[bool, str]:
        """Check if terminal size is adequate"""
        height, width = self.stdscr.getmaxyx()
        if height < self.min_height or width < self.min_width:
            return False, f"Terminal too small. Min size: {self.min_width}x{self.min_height}, Current: {width}x{height}"
        return True, ""

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
        header = "Process Viewer (inspired by k9s)"
        self.safe_addstr(0, 0, "═" * width, curses.color_pair(1))
        self.safe_addstr(1, 2, f"{header:^{width-4}}", curses.color_pair(2) | curses.A_BOLD)
        self.safe_addstr(2, 0, "═" * width, curses.color_pair(1))

    def draw_process_list(self, processes, selected_idx, max_rows):
        start_y = self.header_height + 1
        # Adjust list height to leave space for status and help
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

    def draw_status_bar(self, width, sort_by, search_term):
        max_y = self.stdscr.getmaxyx()[0]
        status = f"Sort: {sort_by.upper()}"
        if search_term:
            status += f" | Search: {search_term}"
        self.safe_addstr(max_y - 2, 0, f"{status:<{width}}", curses.color_pair(2) | curses.A_BOLD)

    def draw_help(self, width):
        max_y = self.stdscr.getmaxyx()[0]
        help_text = "q:Quit | ↑/↓:Navigate | s:Sort | /:Search | Enter:Details"
        self.safe_addstr(max_y - 1, 0, f"{help_text:<{width}}", curses.color_pair(1))

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
