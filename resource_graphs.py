import psutil
from collections import deque
from datetime import datetime
from typing import List, Tuple

class ResourceHistory:
    def __init__(self, max_points=60):
        self.max_points = max_points
        self.cpu_history = deque(maxlen=max_points)
        self.memory_history = deque(maxlen=max_points)
        self.timestamps = deque(maxlen=max_points)
        
    def update(self):
        """Update resource history with current values"""
        cpu = psutil.cpu_percent(interval=0)
        memory = psutil.virtual_memory().percent
        timestamp = datetime.now()
        
        self.cpu_history.append(cpu)
        self.memory_history.append(memory)
        self.timestamps.append(timestamp)

    def get_cpu_graph(self, width: int, height: int) -> List[str]:
        """Generate ASCII graph for CPU usage"""
        return self._generate_graph(list(self.cpu_history), width, height, "CPU Usage %")

    def get_memory_graph(self, width: int, height: int) -> List[str]:
        """Generate ASCII graph for memory usage"""
        return self._generate_graph(list(self.memory_history), width, height, "Memory Usage %")

    def _generate_graph(self, data: List[float], width: int, height: int, title: str) -> List[str]:
        """Generate ASCII graph from data points"""
        if not data:
            return [" " * width] * height

        # Calculate graph dimensions
        graph_height = height - 2  # Reserve space for title and labels
        graph_width = width - 6    # Reserve space for y-axis labels

        # Scale data to graph height
        max_value = max(data + [100])  # Include 100 to maintain scale
        min_value = min(data + [0])    # Include 0 to maintain scale
        scale = graph_height / (max_value - min_value) if max_value > min_value else 1

        # Generate graph lines
        lines = []
        
        # Add title
        lines.append(f"{title:^{width}}")

        # Generate graph body
        for y in range(graph_height):
            value = max_value - (y / scale)
            line = f"{value:4.0f}│"
            
            for x in range(min(len(data), graph_width)):
                data_idx = x - graph_width
                data_value = data[data_idx]
                height_at_x = (data_value - min_value) * scale
                
                if graph_height - y <= height_at_x:
                    line += "█"
                else:
                    line += " "
            
            lines.append(line)

        # Add x-axis
        lines.append("    └" + "─" * graph_width)

        return lines
