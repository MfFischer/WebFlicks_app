from flask import Flask, request, jsonify, render_template
from datamanager.sqlite_data_manager import SQLiteDataManager

# Initialize the Flask application
app = Flask(__name__)

# Initialize the SQLiteDataManager with the database path
data_manager = SQLiteDataManager('moviwebgit addapp.db')  # Use the appropriate path to your database


@app.route('/')
def home():
    return "Welcome to MovieWeb App!"


@app.route('/users', methods=['GET'])
def get_users():
    users = data_manager.get_all_users()
    # Convert the list of tuples to a list of dictionaries for JSON response
    users_list = [{'id': user[0], 'name': user[1]} for user in users]
    return jsonify(users_list)


@app.route('/users', methods=['POST'])
def add_user():
    user_name = request.json.get('name')
    if not user_name:
        return jsonify({"error": "Name is required"}), 400
    user_id = data_manager.add_user(user_name)
    return jsonify({"id": user_id, "name": user_name}), 201


# New route for listing users as a string
@app.route('/users')
def list_users():
    users = data_manager.get_all_users()
    print(users)  # Print users to the console for debugging
    return render_template('users.html', users=users)


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
