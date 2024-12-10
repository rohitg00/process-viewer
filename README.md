# Process Viewer

A terminal-based process visualization tool providing real-time system process monitoring and management capabilities.

## Features

- Real-time process monitoring with CPU/Memory usage graphs
- Process tree visualization with parent-child relationships
- Multi-criteria sorting (CPU, Memory, PID, Name)
- Process filtering by status, CPU/Memory thresholds, and username
- Interactive search functionality
- Dynamic terminal size adaptation
- ASCII-based resource utilization graphs
- Auto-scaling graph displays

## Requirements

- Python 3.11 or higher
- psutil >= 6.1.0
- curses-menu >= 0.7.0

## Installation

```bash
pip install process-viewer
```

## Usage

After installation, you can run the process viewer using:

```bash
process-viewer
```

Or run directly from the source:

```bash
python main.py
```

## Keyboard Shortcuts

- `↑/↓`: Navigate through processes
- `s`: Toggle sort mode (CPU/Memory/PID/Name)
- `/`: Enter search mode
- `f`: Open filter menu
- `c`: Clear all filters
- `t`: Toggle tree/flat view
- `Enter`: View process details
- `x`: Terminate selected process
- `q`: Quit application

## Filter Menu Options

1. Filter by Status (r: running, s: sleeping, t: stopped, z: zombie)
2. Filter by CPU Usage threshold
3. Filter by Memory Usage threshold
4. Filter by Username

## Development

To set up the development environment:

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## License

This project is open-source and available under the MIT License.
