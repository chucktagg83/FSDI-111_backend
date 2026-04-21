# Import tools from Flask
from flask import Flask, jsonify, request

# Import SQLite (built-in database)
import sqlite3

# Create the Flask app
app = Flask(__name__)

# Name of the database file (will be created if it doesn't exist)
DB_NAME = "budget_manager.db"


# Function to initialize (set up) the database
def init_db():
    # Open a connection to the database
    connection = sqlite3.connect(DB_NAME)
    
    # Create a cursor (used to run SQL commands)
    cursor = connection.cursor()
    
# Create a table called "users" if it doesn't already exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,  
            username TEXT UNIQUE NOT NULL,         
            password TEXT NOT NULL                
        )       
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT NOT NULL,
            amount INTEGER NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    
    
    # Save changes to the database
    connection.commit()
    
    # Close the database connection
    connection.close()


# ------------------ HEALTH CHECK ROUTE ------------------

# GET request to check if server is running
@app.get('/api/health')
def health_check():
    # Return a simple JSON response
    return jsonify({
        "status": "OK"
    }), 200  # 200 = success


# ------------------ USERS ROUTE ------------------

# POST request to create/register a new user
@app.post('/api/users')
def register():
    
    # Get JSON data sent from client (frontend/Postman)
    new_user = request.get_json()
    
    # Print data in terminal (for debugging)
    print(new_user)
    
    # Extract username and password from request body
    username = new_user["username"]
    password = new_user["password"]
    
    # Connect to the database
    connection = sqlite3.connect(DB_NAME)
    
    # Create cursor to run SQL commands
    cursor = connection.cursor()
    
    # Insert new user into database
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)  # prevents SQL injection
    )
    
    # Save changes
    connection.commit()
    
    # Close connection
    connection.close()
    
    # Send success response
    return jsonify({
        "success": True,
        "message": "User record updated!"
    }), 201  # 201 = created
    
# ------------------ EXPENSES -----------------
@app.post('/api/expenses')
def create_expense():
    new_expense = request.get_json()
    print(new_expense)
    
    title = new_expense["title"]
    description = new_expense["description"]
    amount = new_expense["amount"]
    date = new_expense["date"]
    category = new_expense["category"]
    user_id = new_expense["user_id"]
    
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO expenses (title, description, amount, date, category, user_id)
        VALUES (?, ?, ?, ?, ?, ?)""", (title, description, amount, date, category, user_id))
    connection.commit()
    connection.close()
    
    
    return jsonify({
        "success": True,
        "message": "Expense created successfully"
    }), 201


# ------------------ RUN APP ------------------

# This ensures the app runs only when this file is executed directly
if __name__ == "__main__":
    
    # Initialize database (create table if needed)
    init_db()
    # Run the Flask server in debug mode
    app.run(debug=True)