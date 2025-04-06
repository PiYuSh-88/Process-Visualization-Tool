from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import time
from process_scheduler import ProcessScheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Initialize the process scheduler
scheduler = ProcessScheduler()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/processes', methods=['GET'])
def get_processes():
    return jsonify(scheduler.get_processes())

@app.route('/api/processes', methods=['POST'])
def add_process():
    try:
        data = request.json
        burst_time = data.get('burst_time')
        arrival_time = data.get('arrival_time')
        priority = data.get('priority', 0)  # Add priority parameter
        
        if burst_time is None or arrival_time is None:
            return jsonify({
                "status": "error",
                "message": "Missing required fields"
            }), 400
        
        scheduler.add_process(burst_time, arrival_time, priority)
        # Send updated state after adding process
        socketio.emit('state_update', scheduler.get_current_state())
        
        return jsonify({
            "status": "success",
            "message": "Process added successfully",
            "processes": scheduler.get_processes()
        })
    except Exception as e:
        print(f"Error adding process: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to add process: {str(e)}"
        }), 500

@app.route('/api/processes/<int:pid>', methods=['PUT'])
def update_process(pid):
    try:
        data = request.json
        burst_time = data.get('burst_time')
        arrival_time = data.get('arrival_time')
        priority = data.get('priority', 0)
        
        if burst_time is None or arrival_time is None:
            return jsonify({
                "status": "error",
                "message": "Missing required fields"
            }), 400
        
        success = scheduler.update_process(pid, burst_time, arrival_time, priority)
        if success:
            # Send updated state after updating process
            socketio.emit('state_update', scheduler.get_current_state())
            return jsonify({
                "status": "success",
                "message": "Process updated successfully",
                "processes": scheduler.get_processes()
            })
        return jsonify({
            "status": "error",
            "message": "Process not found"
        }), 404
    except Exception as e:
        print(f"Error updating process: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to update process: {str(e)}"
        }), 500

@app.route('/api/processes/<int:pid>', methods=['DELETE'])
def delete_process(pid):
    try:
        success = scheduler.delete_process(pid)
        if success:
            # Send updated state after deleting process
            socketio.emit('state_update', scheduler.get_current_state())
            return jsonify({
                "status": "success",
                "message": "Process deleted successfully",
                "processes": scheduler.get_processes()
            })
        return jsonify({
            "status": "error",
            "message": "Process not found"
        }), 404
    except Exception as e:
        print(f"Error deleting process: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to delete process: {str(e)}"
        }), 500

@app.route('/api/processes/generate', methods=['POST'])
def generate_processes():
    try:
        count = request.json.get('count', 5)
        scheduler.generate_random_processes(count)
        # Send updated state after generating processes
        socketio.emit('state_update', scheduler.get_current_state())
        return jsonify({
            "status": "success",
            "message": f"Generated {count} random processes",
            "processes": scheduler.get_processes()
        })
    except Exception as e:
        print(f"Error generating processes: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to generate processes: {str(e)}"
        }), 500

@app.route('/api/start', methods=['POST'])
def start_simulation():
    try:
        data = request.json
        algorithm = data.get('algorithm', 'fcfs')
        
        # Check if there are any processes
        if not scheduler.processes:
            return jsonify({
                "status": "error",
                "message": "No processes available. Please add processes first."
            }), 400
        
        # Set algorithm and start simulation
        scheduler.set_algorithm(algorithm)
        scheduler.start()
        
        # Send initial state
        socketio.emit('state_update', scheduler.get_current_state())
        
        return jsonify({
            "status": "success",
            "message": f"Simulation started with {algorithm} algorithm",
            "state": scheduler.get_current_state()
        })
    except Exception as e:
        print(f"Error starting simulation: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to start simulation: {str(e)}"
        }), 500

@app.route('/api/pause', methods=['POST'])
def pause_simulation():
    try:
        scheduler.pause()
        return jsonify({
            "status": "success",
            "message": "Simulation paused"
        })
    except Exception as e:
        print(f"Error pausing simulation: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to pause simulation: {str(e)}"
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_simulation():
    try:
        scheduler.reset()
        # Send updated state after reset
        socketio.emit('state_update', scheduler.get_current_state())
        return jsonify({
            "status": "success",
            "message": "Simulation reset"
        })
    except Exception as e:
        print(f"Error resetting simulation: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to reset simulation: {str(e)}"
        }), 500

@app.route('/api/step', methods=['POST'])
def step_simulation():
    try:
        scheduler.step()
        return jsonify(scheduler.get_current_state())
    except Exception as e:
        print(f"Error stepping simulation: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to step simulation: {str(e)}"
        }), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send initial state to new client
    emit('state_update', scheduler.get_current_state())

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True) 
