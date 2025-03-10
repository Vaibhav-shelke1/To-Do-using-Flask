from flask import Flask, request, jsonify
from db import get_db, close_db, init_db_command
import sqlite3

app = Flask(__name__)
app.config['DATABASE'] = 'instance/todo.db'  
app.cli.add_command(init_db_command)

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/addTask', methods=['POST'])
def add_task():
    try:
        data = request.json  
        if not data or 'task' not in data:
            return jsonify({"error": "Task content is required"}), 400

        db = get_db()
        db.execute("INSERT INTO Task (task) VALUES (?)", (data['task'],))
        db.commit()

        return jsonify({"message": "Task added successfully"}), 201

    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route('/getTasks', methods=['GET'])
def get_tasks():
    try:
        db = get_db()
        tasks = db.execute("SELECT * FROM Task").fetchall()

        return jsonify([dict(task) for task in tasks])

    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route('/deleteTask/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
   
    try:
        db = get_db()
        result = db.execute("DELETE FROM Task WHERE id = ?", (task_id,))
        db.commit()

        if result.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"message": "Task deleted successfully"})

    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route('/updateTask/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        data = request.json  
        if not data or 'task' not in data:
            return jsonify({"error": "Task content is required"}), 400

        db = get_db()
        result = db.execute("UPDATE Task SET task = ? WHERE id = ?", (data['task'], task_id))
        db.commit()

        if result.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"message": "Task updated successfully"})

    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.teardown_appcontext
def close_database(exception):
    close_db()

