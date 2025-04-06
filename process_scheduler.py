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
        self.completion_time = 0
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
        self.quantum_counter = 0

    def add_process(self, burst_time: int, arrival_time: int, priority: int = 0) -> Process:
        """Add a new process to the scheduler."""
        process = Process(self.next_pid, burst_time, arrival_time)
        process.priority = priority
        self.processes.append(process)
        self.next_pid += 1
        self.processes.sort(key=lambda x: x.arrival_time)
        return process

    def update_process(self, pid: int, burst_time: int, arrival_time: int, priority: int = 0) -> bool:
        """Update an existing process's burst time, arrival time, and priority."""
        for process in self.processes:
            if process.pid == pid:
                process.burst_time = burst_time
                process.arrival_time = arrival_time
                process.remaining_time = burst_time
                process.priority = priority
                self.processes.sort(key=lambda x: x.arrival_time)
                return True
        return False

    def delete_process(self, pid: int) -> bool:
        """Delete a process from the scheduler and clean up all queues."""
        for i, process in enumerate(self.processes):
            if process.pid == pid:
                # Remove from all queues
                if pid in self.ready_queue:
                    self.ready_queue.remove(pid)
                if pid in self.waiting_queue:
                    self.waiting_queue.remove(pid)
                if pid in self.completed_processes:
                    self.completed_processes.remove(pid)
                # If this is the current process, clear it
                if self.current_process and self.current_process.pid == pid:
                    self.current_process = None
                # Remove from processes list
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
        self.quantum_counter = 0
        for process in self.processes:
            process.state = ProcessState.NEW
            process.remaining_time = process.burst_time
            process.waiting_time = 0
            process.turnaround_time = 0
            process.completion_time = 0
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
        """Update process states based on arrival time and current time."""
        # Update arrival of new processes
        for process in self.processes:
            if process.state == ProcessState.NEW:
                if process.arrival_time <= self.current_time:
                    process.state = ProcessState.READY
                    if process.pid not in self.ready_queue:
                        self.ready_queue.append(process.pid)
                else:
                    process.state = ProcessState.WAITING
                    if process.pid not in self.waiting_queue:
                        self.waiting_queue.append(process.pid)
            elif process.state == ProcessState.WAITING and process.arrival_time <= self.current_time:
                process.state = ProcessState.READY
                if process.pid in self.waiting_queue:
                    self.waiting_queue.remove(process.pid)
                if process.pid not in self.ready_queue:
                    self.ready_queue.append(process.pid)
            elif process.state == ProcessState.READY:
                # Ensure process is in ready queue
                if process.pid not in self.ready_queue:
                    self.ready_queue.append(process.pid)
                # Remove from waiting queue if present
                if process.pid in self.waiting_queue:
                    self.waiting_queue.remove(process.pid)

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

    def _fcfs_schedule(self):
        """First Come First Serve scheduling algorithm."""
        if not self.current_process or self.current_process.state == ProcessState.TERMINATED:
            if self.ready_queue:
                # Get the first process from ready queue (already sorted by arrival time)
                pid = self.ready_queue.pop(0)
                self.current_process = next(p for p in self.processes if p.pid == pid)
                self.current_process.state = ProcessState.RUNNING
                if self.current_process.start_time is None:
                    # Set start time to current time
                    self.current_process.start_time = self.current_time
                    # Calculate waiting time: WT = ST - AT
                    self.current_process.waiting_time = max(0, self.current_time - self.current_process.arrival_time)

        if self.current_process:
            self.current_process.remaining_time -= 1
            if self.current_process.remaining_time <= 0:
                self.current_process.state = ProcessState.TERMINATED
                self.current_process.end_time = self.current_time + 1  # End at next time unit
                # Calculate completion time: CT = ST + BT
                self.current_process.completion_time = self.current_process.start_time + self.current_process.burst_time
                # Calculate turnaround time: TAT = CT - AT
                self.current_process.turnaround_time = self.current_process.completion_time - self.current_process.arrival_time
                # Add to completed processes
                self.completed_processes.append(self.current_process.pid)
                self.current_process = None

    def _sjf_schedule(self):
        if not self.current_process or self.current_process.state == ProcessState.TERMINATED:
            if self.ready_queue:
                # Sort ready queue by remaining time
                self.ready_queue.sort(key=lambda pid: next(p for p in self.processes if p.pid == pid).remaining_time)
                pid = self.ready_queue.pop(0)
                self.current_process = next(p for p in self.processes if p.pid == pid)
                self.current_process.state = ProcessState.RUNNING
                if self.current_process.start_time is None:
                    # Set start time to current time
                    self.current_process.start_time = self.current_time
                    # Calculate waiting time: WT = ST - AT
                    self.current_process.waiting_time = self.current_time - self.current_process.arrival_time

        if self.current_process:
            self.current_process.remaining_time -= 1
            if self.current_process.remaining_time <= 0:
                self.current_process.state = ProcessState.TERMINATED
                self.current_process.end_time = self.current_time
                # Calculate completion time: CT = ST + BT
                self.current_process.completion_time = self.current_process.start_time + self.current_process.burst_time
                self.completed_processes.append(self.current_process.pid)
                self.current_process = None

    def _rr_schedule(self):
        """Round Robin scheduling algorithm."""
        if not self.current_process or self.current_process.state == ProcessState.TERMINATED:
            if self.ready_queue:
                # Get the next process from ready queue
                pid = self.ready_queue.pop(0)
                self.current_process = next(p for p in self.processes if p.pid == pid)
                self.current_process.state = ProcessState.RUNNING
                if self.current_process.start_time is None:
                    # Set start time to current time
                    self.current_process.start_time = self.current_time
                    # Calculate waiting time: WT = ST - AT
                    self.current_process.waiting_time = max(0, self.current_time - self.current_process.arrival_time)
                # Reset quantum counter when process starts
                self.quantum_counter = 0

        if self.current_process:
            self.current_process.remaining_time -= 1
            self.quantum_counter += 1
            if self.current_process.remaining_time <= 0:
                self.current_process.state = ProcessState.TERMINATED
                self.current_process.end_time = self.current_time + 1  # End at next time unit
                # Calculate completion time: CT = ST + BT
                self.current_process.completion_time = self.current_process.start_time + self.current_process.burst_time
                # Calculate turnaround time: TAT = CT - AT
                self.current_process.turnaround_time = self.current_process.completion_time - self.current_process.arrival_time
                self.completed_processes.append(self.current_process.pid)
                self.current_process = None
            elif self.quantum_counter >= self.quantum:  # Time quantum expired
                # Move current process to end of ready queue
                self.current_process.state = ProcessState.READY
                if self.current_process.pid not in self.ready_queue:
                    self.ready_queue.append(self.current_process.pid)
                self.current_process = None
                # Reset quantum counter for next process
                self.quantum_counter = 0

    def _priority_schedule(self):
        if not self.current_process or self.current_process.state == ProcessState.TERMINATED:
            if self.ready_queue:
                # Sort by priority (lower number = higher priority)
                self.ready_queue.sort(key=lambda pid: next(p for p in self.processes if p.pid == pid).priority)
                pid = self.ready_queue.pop(0)
                self.current_process = next(p for p in self.processes if p.pid == pid)
                self.current_process.state = ProcessState.RUNNING
                if self.current_process.start_time is None:
                    # Set start time to current time
                    self.current_process.start_time = self.current_time
                    # Calculate waiting time: WT = ST - AT
                    self.current_process.waiting_time = self.current_time - self.current_process.arrival_time

        if self.current_process:
            self.current_process.remaining_time -= 1
            if self.current_process.remaining_time <= 0:
                self.current_process.state = ProcessState.TERMINATED
                self.current_process.end_time = self.current_time
                # Calculate completion time: CT = ST + BT
                self.current_process.completion_time = self.current_process.start_time + self.current_process.burst_time
                self.completed_processes.append(self.current_process.pid)
                self.current_process = None
            elif self.preemptive and self.ready_queue:
                # Check if a higher priority process has arrived
                highest_pid = min(self.ready_queue, key=lambda pid: next(p for p in self.processes if p.pid == pid).priority)
                highest_priority = next(p for p in self.processes if p.pid == highest_pid)
                if highest_priority.priority < self.current_process.priority:
                    self.current_process.state = ProcessState.READY
                    if self.current_process.pid not in self.ready_queue:
                        self.ready_queue.append(self.current_process.pid)
                    self.current_process = highest_priority
                    if highest_pid in self.ready_queue:
                        self.ready_queue.remove(highest_pid)
                    self.current_process.state = ProcessState.RUNNING
                    if self.current_process.start_time is None:
                        # Set start time to current time
                        self.current_process.start_time = self.current_time
                        # Calculate waiting time: WT = ST - AT
                        self.current_process.waiting_time = self.current_time - self.current_process.arrival_time

    def _sjf_preemptive_schedule(self):
        """Shortest Job First Preemptive scheduling algorithm."""
        if not self.current_process or self.current_process.state == ProcessState.TERMINATED:
            if self.ready_queue:
                # Sort by remaining time
                self.ready_queue.sort(key=lambda pid: next(p for p in self.processes if p.pid == pid).remaining_time)
                pid = self.ready_queue.pop(0)
                self.current_process = next(p for p in self.processes if p.pid == pid)
                self.current_process.state = ProcessState.RUNNING
                if self.current_process.start_time is None:
                    self.current_process.start_time = self.current_time
                    # Calculate waiting time when process first starts running
                    self.current_process.waiting_time = max(0, self.current_time - self.current_process.arrival_time)

        if self.current_process:
            self.current_process.remaining_time -= 1
            if self.current_process.remaining_time <= 0:
                self.current_process.state = ProcessState.TERMINATED
                self.current_process.end_time = self.current_time + 1  # End at next time unit
                # Calculate completion time: CT = ST + BT
                self.current_process.completion_time = self.current_process.start_time + self.current_process.burst_time
                # Calculate turnaround time: TAT = CT - AT
                self.current_process.turnaround_time = self.current_process.completion_time - self.current_process.arrival_time
                self.completed_processes.append(self.current_process.pid)
                self.current_process = None
            elif self.preemptive and self.ready_queue:
                # Check if a shorter job has arrived
                shortest_pid = min(self.ready_queue, key=lambda pid: next(p for p in self.processes if p.pid == pid).remaining_time)
                shortest_job = next(p for p in self.processes if p.pid == shortest_pid)
                if shortest_job.remaining_time < self.current_process.remaining_time:
                    # Preempt current process
                    self.current_process.state = ProcessState.READY
                    if self.current_process.pid not in self.ready_queue:
                        self.ready_queue.append(self.current_process.pid)
                    # Switch to shorter job
                    self.current_process = shortest_job
                    if shortest_pid in self.ready_queue:
                        self.ready_queue.remove(shortest_pid)
                    self.current_process.state = ProcessState.RUNNING
                    if self.current_process.start_time is None:
                        self.current_process.start_time = self.current_time
                        # Calculate waiting time when process first starts running
                        self.current_process.waiting_time = max(0, self.current_time - self.current_process.arrival_time)

    def _update_metrics(self):
        """Update performance metrics for all processes."""
        total_waiting_time = 0
        total_turnaround_time = 0
        total_response_time = 0
        completed_count = len(self.completed_processes)

        for process in self.processes:
            if process.state == ProcessState.TERMINATED:
                # Turnaround time: TAT = CT - AT
                process.turnaround_time = process.completion_time - process.arrival_time
                
                # Waiting time: WT = TAT - BT
                process.waiting_time = max(0, process.turnaround_time - process.burst_time)
                
                total_waiting_time += process.waiting_time
                total_turnaround_time += process.turnaround_time
                if process.start_time is not None:
                    # Response time: RT = ST - AT
                    response_time = max(0, process.start_time - process.arrival_time)
                    total_response_time += response_time

        # Calculate average metrics
        if completed_count > 0:
            avg_waiting_time = total_waiting_time / completed_count
            avg_turnaround_time = total_turnaround_time / completed_count
            avg_response_time = total_response_time / completed_count
            
            # Ensure no negative values
            avg_waiting_time = max(0, avg_waiting_time)
            avg_turnaround_time = max(0, avg_turnaround_time)
            avg_response_time = max(0, avg_response_time)
        else:
            avg_waiting_time = 0
            avg_turnaround_time = 0
            avg_response_time = 0

        return {
            'avg_waiting_time': avg_waiting_time,
            'avg_turnaround_time': avg_turnaround_time,
            'avg_response_time': avg_response_time
        }

    def get_current_state(self):
        """Get the current state of the scheduler for visualization."""
        return {
            'processes': [
                {
                    'pid': p.pid,
                    'burst_time': p.burst_time,
                    'arrival_time': p.arrival_time,
                    'state': p.state.value,
                    'waiting_time': p.waiting_time,
                    'turnaround_time': p.turnaround_time,
                    'completion_time': p.completion_time,
                    'priority': p.priority
                }
                for p in self.processes
            ],
            'ready_queue': self.ready_queue,  # Already a list of PIDs
            'waiting_queue': self.waiting_queue,  # Already a list of PIDs
            'completed_processes': self.completed_processes,  # Already a list of PIDs
            'performance_metrics': self._update_metrics()
        }

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
            'completion_time': p.completion_time,
            'priority': p.priority
        } for p in self.processes]

    def get_performance_metrics(self) -> Dict:
        """Calculate and return performance metrics."""
        completed = [p for p in self.processes if p.state == ProcessState.TERMINATED]
        if not completed:
            return {
                'avg_waiting_time': 0,
                'avg_turnaround_time': 0,
                'avg_response_time': 0
            }

        total_waiting_time = sum(p.waiting_time for p in completed)
        total_turnaround_time = sum(p.turnaround_time for p in completed)
        total_response_time = sum(p.start_time - p.arrival_time for p in completed if p.start_time is not None)
        total_burst_time = sum(p.burst_time for p in completed)
        total_time = max(p.end_time for p in completed) if completed else 0

        return {
            'avg_waiting_time': total_waiting_time / len(completed),
            'avg_turnaround_time': total_turnaround_time / len(completed),
            'avg_response_time': total_response_time / len(completed)
        } 