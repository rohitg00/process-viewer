import curses

def handle_input(key, selected_idx, process_count, search_term, sort_by):
    # Navigation
    if key == curses.KEY_UP and selected_idx > 0:
        return (selected_idx - 1, search_term, None)
    elif key == curses.KEY_DOWN and selected_idx < process_count - 1:
        return (selected_idx + 1, search_term, None)

    # Quit
    elif key in (ord('q'), ord('Q')):
        return None

    # Search mode
    elif key == ord('/'):
        search_term = ""
        return (0, search_term, None)

    # Search input
    elif len(search_term) >= 0 and key in (curses.KEY_BACKSPACE, 127):
        search_term = search_term[:-1]
        return (selected_idx, search_term, None)
    elif len(search_term) >= 0 and 32 <= key <= 126:
        search_term += chr(key)
        return (selected_idx, search_term, None)

    # Sort modes
    elif key in (ord('s'), ord('S')):
        sort_options = ['cpu', 'mem', 'pid', 'name']
        current_sort = sort_by if sort_by in sort_options else sort_options[0]
        current_idx = sort_options.index(current_sort)
        new_sort = sort_options[(current_idx + 1) % len(sort_options)]
        return (selected_idx, search_term, new_sort)

    return (selected_idx, search_term, sort_by)
