from flask import Flask, request, jsonify
from db import get_db, close_db, init_db_command

app = Flask(__name__)
app.config['DATABASE'] = 'instance/todo.db'
app.cli.add_command(init_db_command)

@app.route('/')
def home():
    return "Hello, World!"

@app.post('/addTask')
def add_task():
    try:
        data = request.json
        if not data or 'task' not in data:
            return jsonify({"error": "Task content is required"}), 400

        db = get_db()
        db.execute("INSERT INTO Task (task) VALUES (?)", (data['task'],))
        db.commit()

        return jsonify({"message": "Task added successfully"}), 201

    except:
        return jsonify({"error": "An error occurred while processing your request"}), 500

@app.get('/getTasks')
def get_tasks():
    try:
        db = get_db()
        tasks = db.execute("SELECT * FROM Task ORDER BY id DESC").fetchall()

        return jsonify([dict(task) for task in tasks])

    except:
        return jsonify({"error": "An error occurred while fetching tasks"}), 500

@app.delete('/deleteTask/<int:task_id>')
def delete_task(task_id):
    try:
        db = get_db()
        result = db.execute("DELETE FROM Task WHERE id = ?", (task_id,))
        db.commit()

        if result.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"message": "Task deleted successfully"})

    except:
        return jsonify({"error": "An error occurred while deleting the task"}), 500

@app.put('/updateTask/<int:task_id>')
def update_task(task_id):
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        db = get_db()
        fields = []
        values = []

        if "task" in data:
            fields.append("task = ?")
            values.append(data["task"])

        if "status" in data:
            if data["status"] not in ["pending", "complete"]:
                return jsonify({"error": "Invalid status. Use 'pending' or 'complete'"}), 400
            fields.append("status = ?")
            values.append(data["status"])

        if not fields:
            return jsonify({"error": "No valid fields to update"}), 400

        values.append(task_id)
        query = f"UPDATE Task SET {', '.join(fields)} WHERE id = ?"

        result = db.execute(query, values)
        db.commit()

        if db.execute("SELECT changes()").fetchone()[0] == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"message": "Task updated successfully"})

    except Exception as e:
        return jsonify({"error": "An error occurred while updating the task"}), 500


@app.teardown_appcontext
def close_database(exception):
    close_db()
