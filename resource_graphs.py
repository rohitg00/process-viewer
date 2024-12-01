import psutil
from collections import deque
from datetime import datetime
from typing import List, Tuple

class ResourceHistory:
    def __init__(self, max_points=60):
        self.max_points = max(1, max_points)  # Ensure at least 1 point
        self.cpu_history = deque(maxlen=max_points)
        self.memory_history = deque(maxlen=max_points)
        self.timestamps = deque(maxlen=max_points)
        
    def update(self):
        """Update resource history with current values"""
        try:
            cpu = psutil.cpu_percent(interval=0)
            memory = psutil.virtual_memory().percent
            timestamp = datetime.now()
            
            # Ensure values are within valid range
            cpu = max(0, min(100, cpu))
            memory = max(0, min(100, memory))
            
            self.cpu_history.append(cpu)
            self.memory_history.append(memory)
            self.timestamps.append(timestamp)
            return True
        except Exception:
            return False

    def get_cpu_graph(self, width: int, height: int) -> List[str]:
        """Generate ASCII graph for CPU usage"""
        return self._generate_graph(list(self.cpu_history), width, height, "CPU Usage %")

    def get_memory_graph(self, width: int, height: int) -> List[str]:
        """Generate ASCII graph for memory usage"""
        return self._generate_graph(list(self.memory_history), width, height, "Memory Usage %")

    def _generate_graph(self, data: List[float], width: int, height: int, title: str) -> List[str]:
        """Generate ASCII graph from data points"""
        # Ensure positive dimensions
        width = max(10, width)
        height = max(3, height)  # Minimum height for title and axis
        
        # Handle empty data case
        if not data:
            empty_graph = [" " * width for _ in range(height)]
            empty_graph[0] = f"{title} (No data)".center(width)
            return empty_graph

        try:
            # Calculate graph dimensions
            graph_height = max(1, height - 2)  # Reserve space for title and labels
            graph_width = max(4, width - 6)    # Reserve space for y-axis labels

            # Ensure proper bounds and scaling for percentage values
            max_value = 100  # Fixed max for percentage values
            min_value = 0    # Fixed min for percentage values
            value_range = max_value - min_value
            scale = (graph_height - 1) / value_range if value_range > 0 else 1
            
            # Ensure data points are within valid range
            data = [max(min_value, min(max_value, d)) for d in data]

            # Generate graph lines
            lines = []
            
            # Add title
            lines.append(f"{title:^{width}}")

            # Generate graph body
            for y in range(graph_height):
                value = max_value - (y / scale) if scale != 0 else 0
                line = f"{value:4.0f}│"
                
                for x in range(min(len(data), graph_width)):
                    try:
                        data_idx = -(graph_width - x)  # Start from the most recent data
                        if abs(data_idx) <= len(data):
                            data_value = data[data_idx]
                            height_at_x = (data_value - min_value) * scale
                            
                            if graph_height - y <= height_at_x:
                                # Use enhanced gradient effect with custom colors
                                if height_at_x >= graph_height * 0.8:
                                    line += "▆"  # Full block for high values
                                elif height_at_x >= graph_height * 0.6:
                                    line += "▅"  # High-medium block
                                elif height_at_x >= graph_height * 0.4:
                                    line += "▄"  # Medium block
                                elif height_at_x >= graph_height * 0.2:
                                    line += "▃"  # Low block
                                else:
                                    line += "▂"  # Very low block
                            else:
                                line += " "
                        else:
                            line += " "
                    except IndexError:
                        line += " "
                
                lines.append(line)

            # Add x-axis
            lines.append("    └" + "─" * graph_width)

            return lines
            
        except Exception:
            # Fallback to empty graph on error
            empty_graph = [" " * width for _ in range(height)]
            empty_graph[0] = f"{title} (Error)".center(width)
            return empty_graph
