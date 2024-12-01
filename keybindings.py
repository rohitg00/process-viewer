import curses

def handle_input(key, state):
    selected_idx = state['selected_idx']
    process_count = state['process_count']
    search_term = state['search_term']
    sort_by = state['sort_by']
    filters = state['filters']
    input_mode = state['input_mode']
    
    # Get the current process if needed
    current_process = None
    if process_count > 0 and selected_idx >= 0:
        current_process = state.get('processes', [])[selected_idx] if state.get('processes') else None

    # Navigation
    if input_mode == 'normal':
        if key == curses.KEY_UP and selected_idx > 0:
            state['selected_idx'] = selected_idx - 1
        elif key == curses.KEY_DOWN and selected_idx < process_count - 1:
            state['selected_idx'] = selected_idx + 1
        elif key == ord('\n'):  # Enter key
            if current_process:
                state['input_mode'] = 'details'
        elif key == ord('x'):
            if current_process:
                state['input_mode'] = 'confirm_terminate'
        
        # Quit
        elif key in (ord('q'), ord('Q')):
            return None
        
        # Search mode
        elif key == ord('/'):
            state['input_mode'] = 'search'
            state['search_term'] = ""
        
        # Sort modes
        elif key in (ord('s'), ord('S')):
            sort_options = ['cpu', 'mem', 'pid', 'name']
            current_idx = sort_options.index(sort_by if sort_by in sort_options else sort_options[0])
            state['sort_by'] = sort_options[(current_idx + 1) % len(sort_options)]
        
        # Filter controls
        elif key == ord('f'):
            state['input_mode'] = 'filter_menu'
        elif key == ord('c'):
            state['filters'] = {'status': None, 'min_cpu': None, 'min_memory': None, 'user_filter': None}
        elif key == ord('t'):
            state['tree_view'] = not state['tree_view']
            state['selected_idx'] = 0  # Reset selection when switching views
    
    # Search input mode
    elif input_mode == 'search':
        if key in (curses.KEY_BACKSPACE, 127):
            state['search_term'] = search_term[:-1]
        elif key == 27:  # ESC
            state['input_mode'] = 'normal'
        elif 32 <= key <= 126:
            state['search_term'] = search_term + chr(key)
    
    # Filter menu mode
    elif input_mode == 'filter_menu':
        if key == 27:  # ESC
            state['input_mode'] = 'normal'
        elif key in (ord('1'), ord('2'), ord('3'), ord('4')):
            state['input_mode'] = f'filter_{chr(key)}'
        elif key == ord('c'):  # Clear filters
            state['filters'] = {'status': None, 'min_cpu': None, 'min_memory': None, 'user_filter': None}
            state['input_mode'] = 'normal'
    
    # Filter input modes
    elif input_mode.startswith('filter_'):
        if key == 27:  # ESC
            state['input_mode'] = 'normal'
        elif key == ord('\n'):  # Enter
            state['input_mode'] = 'normal'
        
        # Status filter
        elif input_mode == 'filter_1':
            if key in (ord('r'), ord('s'), ord('t'), ord('z')):
                state['filters']['status'] = {
                    'r': 'running',
                    's': 'sleeping',
                    't': 'stopped',
                    'z': 'zombie'
                }[chr(key)]
                state['input_mode'] = 'normal'
        
        # CPU/Memory threshold filters
        elif input_mode in ('filter_2', 'filter_3'):
            if key in (curses.KEY_BACKSPACE, 127):
                filter_key = 'min_cpu' if input_mode == 'filter_2' else 'min_memory'
                current = filters.get(filter_key, '')
                if current:
                    new_value = str(current)[:-1]
                    try:
                        state['filters'][filter_key] = float(new_value) if new_value else None
                    except ValueError:
                        pass
            elif 48 <= key <= 57 or key == ord('.'):  # Numbers and decimal point
                filter_key = 'min_cpu' if input_mode == 'filter_2' else 'min_memory'
                current = filters.get(filter_key, '')
                new_value = str(current if current is not None else '') + chr(key)
                try:
                    value = float(new_value)
                    state['filters'][filter_key] = value
                except ValueError:
                    pass
        
        # Username filter
        elif input_mode == 'filter_4':
            if key in (curses.KEY_BACKSPACE, 127):
                current = filters.get('user_filter', '')
                state['filters']['user_filter'] = current[:-1] if current else None
            elif 32 <= key <= 126:  # Printable characters
                current = filters.get('user_filter', '')
                state['filters']['user_filter'] = (current if current else '') + chr(key)
    
    # Process details mode
    elif input_mode == 'details':
        if key in (27, ord('q')):  # ESC or 'q'
            state['input_mode'] = 'normal'
    
    # Confirmation dialog mode
    elif input_mode == 'confirm_terminate':
        if key == ord('y'):
            if current_process:
                success, message = state['process_manager'].terminate_process(current_process['pid'])
                state['status_message'] = message
            state['input_mode'] = 'normal'
        elif key in (ord('n'), 27):  # 'n' or ESC
            state['input_mode'] = 'normal'

    return state
