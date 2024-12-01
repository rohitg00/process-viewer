import curses

class UserInterface:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.header_height = 2
        self.status_height = 1
        self.help_height = 1

    def draw_header(self, width):
        header = "Process Viewer (inspired by k9s)"
        self.stdscr.addstr(0, 0, "=" * width, curses.color_pair(1))
        self.stdscr.addstr(1, 2, f"{header:^{width-4}}", curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.addstr(2, 0, "=" * width, curses.color_pair(1))

    def draw_process_list(self, processes, selected_idx, max_rows):
        start_y = self.header_height + 1
        # Adjust list height to leave space for status and help
        list_height = max_rows - self.header_height - self.status_height - self.help_height - 2
        # Calculate visible window for processes
        window_start = max(0, min(selected_idx - list_height // 2, len(processes) - list_height))
        visible_processes = processes[window_start:window_start + list_height]

        # Draw column headers
        headers = f"{'PID':>8} {'CPU%':>7} {'MEM%':>7} {'STATUS':>10} {'NAME':<20}"
        self.stdscr.addstr(start_y, 2, headers, curses.color_pair(1) | curses.A_BOLD)

        # Draw processes
        for idx, proc in enumerate(visible_processes):
            if start_y + idx + 1 >= max_rows - 2:  # Leave space for status and help
                break

            line = f"{proc['pid']:>8} {proc['cpu_percent']:>7.1f} {proc['memory_percent']:>7.1f} "
            line += f"{proc['status']:>10} {proc['name']:<20}"

            if idx + window_start == selected_idx:
                self.stdscr.addstr(start_y + idx + 1, 2, line, curses.color_pair(3) | curses.A_REVERSE)
            else:
                self.stdscr.addstr(start_y + idx + 1, 2, line, curses.color_pair(1))

    def draw_status_bar(self, width, sort_by, search_term):
        max_y = self.stdscr.getmaxyx()[0]
        status = f"Sort: {sort_by.upper()}"
        if search_term:
            status += f" | Search: {search_term}"
        try:
            self.stdscr.addstr(max_y - 2, 0, f"{status:<{width}}", 
                             curses.color_pair(2) | curses.A_BOLD)
        except curses.error:
            pass

    def draw_help(self, width):
        max_y = self.stdscr.getmaxyx()[0]
        help_text = "q:Quit | ↑/↓:Navigate | s:Sort | /:Search | Enter:Details"
        try:
            self.stdscr.addstr(max_y - 1, 0, f"{help_text:<{width}}", 
                             curses.color_pair(1))
        except curses.error:
            pass
