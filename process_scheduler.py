import random
from enum import Enum
from typing import List, Dict
import time

class ProcessState(Enum):
    NEW = "New"
    READY = "Ready"
    RUNNING = "Running"
    WAITING = "Waiting"
    TERMINATED = "Terminated"

class Process:
    def __init__(self, pid: int, burst_time: int, arrival_time: int):
        self.pid = pid
        self.burst_time = burst_time
        self.arrival_time = arrival_time
        self.remaining_time = burst_time
        self.state = ProcessState.NEW
        self.waiting_time = 0
        self.turnaround_time = 0
        self.start_time = None
        self.end_time = None
        self.priority = 0

class ProcessScheduler:
    def __init__(self):
        self.processes: List[Process] = []
        self.current_time = 0
        self.algorithm = "fcfs"
        self.is_running = False
        self.quantum = 2  # For Round Robin
        self.current_process = None
        self.ready_queue = []
        self.waiting_queue = []
        self.completed_processes = []
        self.next_pid = 0
        self.priority_levels = 5  # For Priority Scheduling
        self.preemptive = True  # For Priority and SJF Preemptive

    def add_process(self, burst_time: int, arrival_time: int, priority: int = 0) -> Process:
        """Add a new process to the scheduler."""
        process = Process(self.next_pid, burst_time, arrival_time)
        process.priority = priority
        self.processes.append(process)
        self.next_pid += 1
        self.processes.sort(key=lambda x: x.arrival_time)
        return process

    def update_process(self, pid: int, burst_time: int, arrival_time: int) -> bool:
        """Update an existing process's burst time and arrival time."""
        for process in self.processes:
            if process.pid == pid:
                process.burst_time = burst_time
                process.arrival_time = arrival_time
                process.remaining_time = burst_time
                self.processes.sort(key=lambda x: x.arrival_time)
                return True
        return False

    def delete_process(self, pid: int) -> bool:
        """Delete a process from the scheduler."""
        for i, process in enumerate(self.processes):
            if process.pid == pid:
                self.processes.pop(i)
                return True
        return False

    def generate_random_processes(self, count: int = 5):
        """Generate random processes with priorities."""
        self.processes = []
        self.next_pid = 0
        for i in range(count):
            burst_time = random.randint(1, 10)
            arrival_time = random.randint(0, 5)
            priority = random.randint(0, self.priority_levels - 1)
            self.add_process(burst_time, arrival_time, priority)

    def set_algorithm(self, algorithm: str):
        self.algorithm = algorithm
        self.reset()

    def start(self):
        self.is_running = True
        self.current_time = 0
        self._update_process_states()

    def pause(self):
        self.is_running = False

    def reset(self):
        self.current_time = 0
        self.is_running = False
        self.current_process = None
        self.ready_queue = []
        self.waiting_queue = []
        self.completed_processes = []
        for process in self.processes:
            process.state = ProcessState.NEW
            process.remaining_time = process.burst_time
            process.waiting_time = 0
            process.turnaround_time = 0
            process.start_time = None
            process.end_time = None

    def step(self):
        if not self.is_running:
            return

        self.current_time += 1
        self._update_process_states()
        self._schedule_next_process()
        self._update_metrics()

    def _update_process_states(self):
        # Update arrival of new processes
        for process in self.processes:
            if process.state == ProcessState.NEW and process.arrival_time <= self.current_time:
                process.state = ProcessState.READY
                self.ready_queue.append(process)

    def _schedule_next_process(self):
        if self.algorithm == "fcfs":
            self._fcfs_schedule()
        elif self.algorithm == "sjf":
            self._sjf_schedule()
        elif self.algorithm == "rr":
            self._rr_schedule()
        elif self.algorithm == "priority":
            self._priority_schedule()
        elif self.algorithm == "sjf_preemptive":
            self._sjf_preemptive_schedule()
        elif self.algorithm == "multilevel_feedback":
            self._multilevel_feedback_schedule()

    def _fcfs_schedule(self):
        if not self.current_process or self.current_process.state == ProcessState.TERMINATED:
            if self.ready_queue:
                self.current_process = self.ready_queue.pop(0)
                self.current_process.state = ProcessState.RUNNING
                if self.current_process.start_time is None:
                    self.current_process.start_time = self.current_time

        if self.current_process:
            self.current_process.remaining_time -= 1
            if self.current_process.remaining_time <= 0:
                self.current_process.state = ProcessState.TERMINATED
                self.current_process.end_time = self.current_time
                self.completed_processes.append(self.current_process)
                self.current_process = None

    def _sjf_schedule(self):
        if not self.current_process or self.current_process.state == ProcessState.TERMINATED:
            if self.ready_queue:
                # Sort ready queue by remaining time
                self.ready_queue.sort(key=lambda x: x.remaining_time)
                self.current_process = self.ready_queue.pop(0)
                self.current_process.state = ProcessState.RUNNING
                if self.current_process.start_time is None:
                    self.current_process.start_time = self.current_time

        if self.current_process:
            self.current_process.remaining_time -= 1
            if self.current_process.remaining_time <= 0:
                self.current_process.state = ProcessState.TERMINATED
                self.current_process.end_time = self.current_time
                self.completed_processes.append(self.current_process)
                self.current_process = None

    def _rr_schedule(self):
        if not self.current_process or self.current_process.state == ProcessState.TERMINATED:
            if self.ready_queue:
                self.current_process = self.ready_queue.pop(0)
                self.current_process.state = ProcessState.RUNNING
                if self.current_process.start_time is None:
                    self.current_process.start_time = self.current_time

        if self.current_process:
            self.current_process.remaining_time -= 1
            if self.current_process.remaining_time <= 0:
                self.current_process.state = ProcessState.TERMINATED
                self.current_process.end_time = self.current_time
                self.completed_processes.append(self.current_process)
                self.current_process = None
            elif self.current_process.remaining_time % self.quantum == 0:
                self.current_process.state = ProcessState.READY
                self.ready_queue.append(self.current_process)
                self.current_process = None

    def _priority_schedule(self):
        if not self.current_process or self.current_process.state == ProcessState.TERMINATED:
            if self.ready_queue:
                # Sort by priority (lower number = higher priority)
                self.ready_queue.sort(key=lambda x: x.priority)
                self.current_process = self.ready_queue.pop(0)
                self.current_process.state = ProcessState.RUNNING
                if self.current_process.start_time is None:
                    self.current_process.start_time = self.current_time

        if self.current_process:
            self.current_process.remaining_time -= 1
            if self.current_process.remaining_time <= 0:
                self.current_process.state = ProcessState.TERMINATED
                self.current_process.end_time = self.current_time
                self.completed_processes.append(self.current_process)
                self.current_process = None
            elif self.preemptive and self.ready_queue:
                # Check if a higher priority process has arrived
                highest_priority = min(self.ready_queue, key=lambda x: x.priority)
                if highest_priority.priority < self.current_process.priority:
                    self.current_process.state = ProcessState.READY
                    self.ready_queue.append(self.current_process)
                    self.current_process = highest_priority
                    self.ready_queue.remove(highest_priority)
                    self.current_process.state = ProcessState.RUNNING

    def _sjf_preemptive_schedule(self):
        if not self.current_process or self.current_process.state == ProcessState.TERMINATED:
            if self.ready_queue:
                # Sort by remaining time
                self.ready_queue.sort(key=lambda x: x.remaining_time)
                self.current_process = self.ready_queue.pop(0)
                self.current_process.state = ProcessState.RUNNING
                if self.current_process.start_time is None:
                    self.current_process.start_time = self.current_time

        if self.current_process:
            self.current_process.remaining_time -= 1
            if self.current_process.remaining_time <= 0:
                self.current_process.state = ProcessState.TERMINATED
                self.current_process.end_time = self.current_time
                self.completed_processes.append(self.current_process)
                self.current_process = None
            elif self.preemptive and self.ready_queue:
                # Check if a shorter job has arrived
                shortest_job = min(self.ready_queue, key=lambda x: x.remaining_time)
                if shortest_job.remaining_time < self.current_process.remaining_time:
                    self.current_process.state = ProcessState.READY
                    self.ready_queue.append(self.current_process)
                    self.current_process = shortest_job
                    self.ready_queue.remove(shortest_job)
                    self.current_process.state = ProcessState.RUNNING

    def _multilevel_feedback_schedule(self):
        # Implementation of Multilevel Feedback Queue scheduling
        # Uses multiple priority queues with different quantum sizes
        if not self.current_process or self.current_process.state == ProcessState.TERMINATED:
            if self.ready_queue:
                # Get process from highest priority queue
                self.current_process = self.ready_queue.pop(0)
                self.current_process.state = ProcessState.RUNNING
                if self.current_process.start_time is None:
                    self.current_process.start_time = self.current_time

        if self.current_process:
            self.current_process.remaining_time -= 1
            if self.current_process.remaining_time <= 0:
                self.current_process.state = ProcessState.TERMINATED
                self.current_process.end_time = self.current_time
                self.completed_processes.append(self.current_process)
                self.current_process = None
            elif self.current_process.remaining_time % self.quantum == 0:
                # Move process to lower priority queue
                self.current_process.state = ProcessState.READY
                self.ready_queue.append(self.current_process)
                self.current_process = None

    def _update_metrics(self):
        for process in self.processes:
            if process.state == ProcessState.READY:
                process.waiting_time += 1
            if process.state == ProcessState.TERMINATED:
                process.turnaround_time = process.end_time - process.arrival_time

    def get_processes(self) -> List[Dict]:
        """Get list of all processes with their current state."""
        return [{
            'pid': p.pid,
            'burst_time': p.burst_time,
            'arrival_time': p.arrival_time,
            'remaining_time': p.remaining_time,
            'state': p.state.value,
            'waiting_time': p.waiting_time,
            'turnaround_time': p.turnaround_time,
            'priority': p.priority
        } for p in self.processes]

    def get_performance_metrics(self) -> Dict:
        """Calculate and return performance metrics."""
        completed = [p for p in self.processes if p.state == ProcessState.TERMINATED]
        if not completed:
            return {
                'avg_waiting_time': 0,
                'avg_turnaround_time': 0,
                'avg_response_time': 0,
                'cpu_utilization': 0,
                'throughput': 0
            }

        total_waiting_time = sum(p.waiting_time for p in completed)
        total_turnaround_time = sum(p.turnaround_time for p in completed)
        total_response_time = sum(p.start_time - p.arrival_time for p in completed if p.start_time is not None)
        total_burst_time = sum(p.burst_time for p in completed)
        total_time = max(p.end_time for p in completed) if completed else 0

        return {
            'avg_waiting_time': total_waiting_time / len(completed),
            'avg_turnaround_time': total_turnaround_time / len(completed),
            'avg_response_time': total_response_time / len(completed),
            'cpu_utilization': (total_burst_time / total_time) * 100 if total_time > 0 else 0,
            'throughput': len(completed) / total_time if total_time > 0 else 0
        }

    def get_current_state(self) -> Dict:
        """Get current state of the scheduler."""
        return {
            'current_time': self.current_time,
            'current_process': self.current_process.pid if self.current_process else None,
            'ready_queue': [p.pid for p in self.ready_queue],
            'waiting_queue': [p.pid for p in self.waiting_queue],
            'completed_processes': [p.pid for p in self.completed_processes],
            'algorithm': self.algorithm,
            'is_running': self.is_running
        } 