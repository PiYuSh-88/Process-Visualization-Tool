document.addEventListener('DOMContentLoaded', () => {
    const visualizer = new ProcessVisualizer();
    let simulationInterval = null;
    let currentSpeed = 'medium';
    let metricsChart = null;

    // DOM Elements
    const startBtn = document.getElementById('start-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const resetBtn = document.getElementById('reset-btn');
    const algorithmSelect = document.getElementById('algorithm-select');
    const speedSelect = document.getElementById('speed-select');
    const addProcessBtn = document.getElementById('add-process-btn');
    const generateRandomBtn = document.getElementById('generate-random-btn');
    const burstTimeInput = document.getElementById('burst-time');
    const arrivalTimeInput = document.getElementById('arrival-time');
    const priorityInput = document.getElementById('priority');
    const processListTable = document.getElementById('process-list-table').getElementsByTagName('tbody')[0];

    // Make editProcess and deleteProcess globally accessible
    window.editProcess = function(pid) {
        const burstTime = prompt('Enter new burst time:');
        const arrivalTime = prompt('Enter new arrival time:');
        const priority = prompt('Enter new priority (0-4):');
        
        if (burstTime !== null && arrivalTime !== null && priority !== null) {
            updateProcess(pid, parseInt(burstTime), parseInt(arrivalTime), parseInt(priority));
        }
    };
    
    window.deleteProcess = function(pid) {
        if (confirm('Are you sure you want to delete this process?')) {
            deleteProcess(pid);
        }
    };

    // Event Listeners
    startBtn.addEventListener('click', startSimulation);
    pauseBtn.addEventListener('click', pauseSimulation);
    resetBtn.addEventListener('click', resetSimulation);
    speedSelect.addEventListener('change', updateSpeed);
    addProcessBtn.addEventListener('click', addProcess);
    generateRandomBtn.addEventListener('click', generateRandomProcesses);

    // Socket.IO event handlers
    socket.on('state_update', (data) => {
        updateVisualization(data);
        updateProcessList(data.processes);
        visualizer.updateProcessTable(data.processes);
        visualizer.updateProcessQueues(data.processes, data.ready_queue, data.waiting_queue, data.completed_processes);
        visualizer.updatePerformanceMetrics(data.performance_metrics);
    });

    // Process Management Functions
    async function addProcess() {
        const burstTime = parseInt(burstTimeInput.value);
        const arrivalTime = parseInt(arrivalTimeInput.value);
        const priority = parseInt(priorityInput.value);

        if (isNaN(burstTime) || isNaN(arrivalTime) || isNaN(priority) || 
            burstTime < 1 || arrivalTime < 0 || priority < 0 || priority > 4) {
            showNotification('error', 'Please enter valid values for burst time, arrival time, and priority');
            return;
        }

        try {
            const response = await fetch('/api/processes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    burst_time: burstTime, 
                    arrival_time: arrivalTime,
                    priority: priority
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                updateProcessList(data.processes);
                // Clear inputs
                burstTimeInput.value = 1;
                arrivalTimeInput.value = 0;
                priorityInput.value = 0;
                showNotification('success', data.message);
            } else {
                showNotification('error', data.message);
            }
        } catch (error) {
            console.error('Error adding process:', error);
            showNotification('error', 'Error adding process');
        }
    }

    async function generateRandomProcesses() {
        try {
            const response = await fetch('/api/processes/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ count: 5 })
            });

            const data = await response.json();
            
            if (response.ok) {
                updateProcessList(data.processes);
                showNotification('success', data.message);
            } else {
                showNotification('error', data.message);
            }
        } catch (error) {
            console.error('Error generating random processes:', error);
            showNotification('error', 'Failed to generate random processes');
        }
    }

    async function updateProcess(pid, burstTime, arrivalTime, priority) {
        try {
            const response = await fetch(`/api/processes/${pid}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    burst_time: burstTime, 
                    arrival_time: arrivalTime,
                    priority: priority
                })
            });

            if (response.ok) {
                const data = await response.json();
                updateProcessList(data.processes);
            } else {
                alert('Failed to update process');
            }
        } catch (error) {
            console.error('Error updating process:', error);
            alert('Error updating process');
        }
    }

    async function deleteProcess(pid) {
        if (!confirm('Are you sure you want to delete this process?')) {
            return;
        }

        try {
            const response = await fetch(`/api/processes/${pid}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                const data = await response.json();
                updateProcessList(data.processes);
            } else {
                alert('Failed to delete process');
            }
        } catch (error) {
            console.error('Error deleting process:', error);
            alert('Error deleting process');
        }
    }

    function updateProcessList(processes) {
        processListTable.innerHTML = processes
            .map(process => `
                <tr>
                    <td>P${process.pid}</td>
                    <td>${process.burst_time}</td>
                    <td>${process.arrival_time}</td>
                    <td>${process.priority}</td>
                    <td class="action-buttons">
                        <button class="edit-btn" onclick="editProcess(${process.pid})">Edit</button>
                        <button class="delete-btn" onclick="deleteProcess(${process.pid})">Delete</button>
                    </td>
                </tr>
            `)
            .join('');
    }

    function updatePerformanceMetrics(metrics) {
        if (!metrics) return;
        
        // Update metric cards
        document.getElementById('avg-waiting-time').textContent = metrics.avg_waiting_time.toFixed(2);
        document.getElementById('avg-turnaround-time').textContent = metrics.avg_turnaround_time.toFixed(2);
        document.getElementById('avg-response-time').textContent = metrics.avg_response_time.toFixed(2);
        document.getElementById('cpu-utilization').textContent = metrics.cpu_utilization.toFixed(2) + '%';
        document.getElementById('throughput').textContent = metrics.throughput.toFixed(2);

        // Update metrics chart
        updateMetricsChart(metrics);
    }

    function updateMetricsChart(metrics) {
        const ctx = document.getElementById('metrics-chart').getContext('2d');
        
        if (metricsChart) {
            metricsChart.destroy();
        }

        metricsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Waiting Time', 'Turnaround Time', 'Response Time', 'CPU Utilization', 'Throughput'],
                datasets: [{
                    label: 'Performance Metrics',
                    data: [
                        metrics.avg_waiting_time,
                        metrics.avg_turnaround_time,
                        metrics.avg_response_time,
                        metrics.cpu_utilization,
                        metrics.throughput
                    ],
                    backgroundColor: [
                        '#e74c3c',
                        '#e67e22',
                        '#f1c40f',
                        '#2ecc71',
                        '#3498db'
                    ]
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // API Functions
    async function startSimulation() {
        const algorithm = algorithmSelect.value;
        try {
            const response = await fetch('/api/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ algorithm })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                startSimulationInterval();
                showNotification('success', data.message);
            } else {
                showNotification('error', data.message);
            }
        } catch (error) {
            console.error('Error starting simulation:', error);
            showNotification('error', 'Failed to start simulation');
        }
    }

    async function pauseSimulation() {
        try {
            const response = await fetch('/api/pause', {
                method: 'POST'
            });
            
            if (response.ok) {
                clearInterval(simulationInterval);
                showNotification('success', 'Simulation paused');
            }
        } catch (error) {
            console.error('Error pausing simulation:', error);
        }
    }

    async function resetSimulation() {
        try {
            const response = await fetch('/api/reset', {
                method: 'POST'
            });
            
            if (response.ok) {
                clearInterval(simulationInterval);
                // Clear visualizations
                visualizer.updateProcessQueues([], [], [], []);
                visualizer.updateProcessTable([]);
                if (metricsChart) {
                    metricsChart.destroy();
                    metricsChart = null;
                }
                showNotification('success', 'Simulation reset');
            }
        } catch (error) {
            console.error('Error resetting simulation:', error);
        }
    }

    function updateSpeed() {
        currentSpeed = speedSelect.value;
        if (simulationInterval) {
            clearInterval(simulationInterval);
            startSimulationInterval();
        }
    }

    function startSimulationInterval() {
        const speeds = {
            'slow': 1000,
            'medium': 500,
            'fast': 100
        };

        clearInterval(simulationInterval);
        simulationInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/step', {
                    method: 'POST'
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data) {
                        updateVisualization(data);
                        updateProcessList(data.processes);
                        updatePerformanceMetrics(data.performance_metrics);
                    }
                }
            } catch (error) {
                console.error('Error stepping simulation:', error);
            }
        }, speeds[currentSpeed]);
    }

    function updateVisualization(data) {
        if (!data) return;
        
        visualizer.updateProcessQueues(
            data.processes,
            data.ready_queue,
            data.waiting_queue,
            data.completed_processes
        );
        visualizer.updateProcessTable(data.processes);
        visualizer.updatePerformanceMetrics(data.performance_metrics);
    }

    // Add notification function
    function showNotification(type, message) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Initial UI state
    updateUIState('disconnected');
}); 