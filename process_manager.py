import psutil
from datetime import datetime

class ProcessManager:
    def __init__(self):
        self.process_list = []

    def get_processes(self, sort_by='cpu'):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                pinfo['cpu_percent'] = proc.cpu_percent()
                pinfo['memory_percent'] = proc.memory_percent()
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Sort processes based on criteria
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        elif sort_by == 'mem':
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        elif sort_by == 'pid':
            processes.sort(key=lambda x: x['pid'])
        elif sort_by == 'name':
            processes.sort(key=lambda x: x['name'].lower())

        return processes

    def filter_processes(self, processes, search_term):
        return [p for p in processes if search_term.lower() in p['name'].lower() or 
                str(p['pid']) == search_term]

    def get_process_details(self, pid):
        try:
            proc = psutil.Process(pid)
            return {
                'pid': pid,
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(),
                'memory_percent': proc.memory_percent(),
                'create_time': datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S'),
                'username': proc.username(),
                'cmdline': ' '.join(proc.cmdline())
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
