# OS Process Scheduler Visualization

A dynamic and interactive process visualization tool for simulating and visualizing process scheduling in an operating system. This project implements various scheduling algorithms and provides real-time visualization of process execution.

## Features

- Multiple Scheduling Algorithms:
  - First Come First Serve (FCFS)
  - Shortest Job First (Non-Preemptive)
  - Shortest Job First (Preemptive)
  - Round Robin
  - Priority Scheduling
  - Multilevel Feedback Queue

- Process Management:
  - Add processes manually
  - Generate random processes
  - Edit process parameters
  - Delete processes

- Real-time Visualization:
  - Process queues (Ready, Waiting, Completed)
  - Performance metrics
  - Process details table

- Performance Metrics:
  - Average Waiting Time
  - Average Turnaround Time
  - Average Response Time
  - CPU Utilization
  - Throughput

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/os-process-scheduler.git
cd os-process-scheduler
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

3. Use the interface to:
   - Add or generate processes
   - Select a scheduling algorithm
   - Control the simulation
   - Monitor performance metrics

## Project Structure

```
os-process-scheduler/
├── main.py              # Flask application
├── process_scheduler.py # Process scheduling logic
├── requirements.txt     # Python dependencies
├── static/             # Static files (CSS, JS)
│   ├── css/
│   └── js/
└── templates/          # HTML templates
```

## Technologies Used

- Python 3.x
- Flask
- Flask-SocketIO
- Chart.js
- HTML5/CSS3
- JavaScript

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Operating System Concepts by Silberschatz, Galvin, and Gagne
- Flask Documentation
- Chart.js Documentation 