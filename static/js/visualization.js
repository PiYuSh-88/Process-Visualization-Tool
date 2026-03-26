class ProcessVisualizer {
    constructor() {
        this.metricsChart = null;
        this.processTable = document.getElementById('process-table').getElementsByTagName('tbody')[0];
        this.readyQueue = document.getElementById('ready-queue');
        this.waitingQueue = document.getElementById('waiting-queue');
        this.completedQueue = document.getElementById('completed-queue');
        
        // Check if metrics chart element exists
        const metricsChartElement = document.getElementById('metrics-chart');
        if (metricsChartElement) {
            this.initializeCharts();
        }
    }

    initializeCharts() {
        // Initialize Metrics Chart
        const metricsCtx = document.getElementById('metrics-chart').getContext('2d');
        this.metricsChart = new Chart(metricsCtx, {
            type: 'bar',
            data: {
                labels: ['Waiting Time', 'Turnaround Time', 'Response Time', 'CPU Utilization', 'Throughput'],
                datasets: [{
                    label: 'Performance Metrics',
                    data: [0, 0, 0, 0, 0],
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

    updateProcessQueues(processes, readyQueue, waitingQueue, completedProcesses) {
        // Update Ready Queue
        this.readyQueue.innerHTML = readyQueue
            .map(pid => this.createProcessElement(processes.find(p => p.pid === pid)))
            .join('');

        // Update Waiting Queue
        this.waitingQueue.innerHTML = waitingQueue
            .map(pid => this.createProcessElement(processes.find(p => p.pid === pid)))
            .join('');

        // Update Completed Queue
        this.completedQueue.innerHTML = completedProcesses
            .map(pid => this.createProcessElement(processes.find(p => p.pid === pid)))
            .join('');
    }

    updateProcessTable(processes) {
        this.processTable.innerHTML = processes
            .map(process => `
                <tr>
                    <td>P${process.pid}</td>
                    <td>${process.burst_time}</td>
                    <td>${process.arrival_time}</td>
                    <td>${process.state}</td>
                    <td>${process.waiting_time || 0}</td>
                    <td>${process.turnaround_time || 0}</td>
                </tr>
            `)
            .join('');
    }

    updatePerformanceMetrics(metrics) {
        if (!metrics) return;

        try {
            // Update metric cards
            document.getElementById('avg-waiting-time').textContent = metrics.avg_waiting_time.toFixed(2);
            document.getElementById('avg-turnaround-time').textContent = metrics.avg_turnaround_time.toFixed(2);
            document.getElementById('avg-response-time').textContent = metrics.avg_response_time.toFixed(2);
            document.getElementById('cpu-utilization').textContent = metrics.cpu_utilization.toFixed(2) + '%';
            document.getElementById('throughput').textContent = metrics.throughput.toFixed(2);

            // Update metrics chart
            if (this.metricsChart) {
                this.metricsChart.data.datasets[0].data = [
                    metrics.avg_waiting_time,
                    metrics.avg_turnaround_time,
                    metrics.avg_response_time,
                    metrics.cpu_utilization,
                    metrics.throughput
                ];
                this.metricsChart.update();
            }
        } catch (error) {
            console.error('Error updating performance metrics:', error);
        }
    }

    createProcessElement(process) {
        if (!process) return '';
        return `
            <div class="process ${process.state.toLowerCase()}">
                P${process.pid}
            </div>
        `;
    }

    getProcessColor(state) {
        const colors = {
            'New': '#95a5a6',
            'Ready': '#3498db',
            'Running': '#2ecc71',
            'Waiting': '#f1c40f',
            'Terminated': '#e74c3c'
        };
        return colors[state] || '#95a5a6';
    }
}