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
    
    
# GET http://127.0.0.1:5000/api/users/
@app.get('/api/users/<int:user_id>')
def get_user_by_id(user_id):
    
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row # Allows columns values to be retrieved by name, row=["username"]
    cursor = connection.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    print(dict(row))
    user_information = dict(row)
    connection.close() # close the connection
    
    return jsonify({
        "success": True,
        "message": "User retrieved successfully",
        "data": user_information
    }), 200 # OK
    
@app.get('/api/users')
def get_users():
    
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row # Allows columns values to be retrieved by name, row=["username"]
    cursor = connection.cursor()
    cursor.execute("SELECT id, username FROM users")
    rows = cursor.fetchall()
    print(rows)
    connection.close()
    
    users = []
    for row in rows:
        print(dict(row))
        users.append(dict(row))
    
    return jsonify({
        "success": True,
        "message": "Users retrieved successfully",
        "data": users
    }), 200
    
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
    user_id = new_expense["expense_id"]
    
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
    
# GET EXPENSES BY USER ID
@app.get('/api/expenses/<int:user_id>')  # Fixed missing ">" in route
def get_expenses(user_id):  # Function receives user_id from URL
    
    connection = sqlite3.connect(DB_NAME)  # Connect to database
    connection.row_factory = sqlite3.Row  # Allow column access by name
    cursor = connection.cursor()  # Create cursor
    
    cursor.execute("SELECT * FROM expenses WHERE user_id=?", (user_id,))  # Get expenses for specific user
    rows = cursor.fetchall()  # Fetch all matching rows (list of results)
    
    if not rows:  # Check if no expenses found
        connection.close()  # Close connection before returning
        return jsonify({
            "success": False,
            "message": "No expenses found for this user"
        }), 404
    
    expenses = [dict(row) for row in rows]  # Convert each row into a dictionary
    
    connection.close()  # Close database connection
    
    return jsonify({  # Return JSON response
        "success": True,  # Boolean (not string)
        "message": "Expenses retrieved successfully",  # Message
        "data": expenses  # Include list of expenses
    }), 200  # HTTP 200 = OK
    
# GET EXPENSES BY ID
@app.get('/api/expenses/<int:expense_id>')  # Define GET route to retrieve all expenses
def get_expense_by_id(expense_id):  # Function to handle request
    
    connection = sqlite3.connect(DB_NAME)  # Connect to database
    connection.row_factory = sqlite3.Row  # Allow column access by name
    cursor = connection.cursor()  # Create cursor
    
    cursor.execute("SELECT * FROM expenses WHERE expense_id=?", (expense_id))  # Get all records from expenses table
    rows = cursor.fetchall()  # Fetch all results (returns a list)    
    
    if not rows:
        connection.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404
        
    connection.close()  # Close database connection
    
    return jsonify({  # Return JSON response
        "success": True,  # Boolean (not string)
        "message": "All expenses retrieved successfully",  # Message
        "data": expenses  # Include the actual list of expenses
    }), 200  # HTTP 200 = OK
    
    
# ---------------------- Updating a Database ------------------------
#Put
@app.put('/api/users/<int:user_id>')
def update_user(user_id):
    updated_user = request.get_json()
    username = updated_user["username"]
    password = updated_user["password"]
    
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    
    # Validation
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        connection.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404
    
    
    cursor.execute("UPDATE users SET username=?, password=? WHERE id=?", (username, password, user_id))
    connection.commit()
    connection.close()
    
    
    return jsonify({
        "success": True,
        "message": "User updated successfully"
    }), 200

# PUT expenses
@app.put('/api/expenses/<int:expense_id>')
def update_expenses_amount(expense_id):
    updated_expense = request.get_json()
    amount = updated_expense["amount"]
    
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    
    # Validation
    cursor.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
    row = cursor.fetchone()
    if not row:
        connection.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404
    
    cursor.execute("UPDATE expenses SET amount=? WHERE id=?", (amount, expense_id))
    connection.commit()
    connection.close()
    
    return jsonify({
        "success": True,
        "message": "User updated successfully"
    }), 200


# --------------------- Deleting A User -----------------------------
#Delete
@app.delete('/api/users/<int:user_id>')
def delete_user(user_id):
    
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    connection.commit()
    connection.close()
    
    return jsonify({
        "success": True,
        "message": "User deleted successfully"
    }), 200
    
# DELETE EXPENSE BY ID
@app.delete('/api/expenses/<int:expense_id>')  # Route to delete expense by ID
def delete_expense(expense_id):  # Function receives expense_id
    
    connection = sqlite3.connect(DB_NAME)  # Connect to database
    cursor = connection.cursor()  # Create cursor
    
    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))  # Delete expense with matching ID
    
    if cursor.rowcount == 0:  # Check if no row was deleted (expense not found)
        connection.close()
        return jsonify({
            "success": False,
            "message": "Expense not found"
        }), 404
    
    connection.commit()  # Save changes
    connection.close()  # Close database connection
    
    return jsonify({
        "success": True,
        "message": "Expense deleted successfully"  # Fixed message (was "User")
    }), 200



# ------------------ RUN APP ------------------

# This ensures the app runs only when this file is executed directly
if __name__ == "__main__":
    
    # Initialize database (create table if needed)
    init_db()
    # Run the Flask server in debug mode
    app.run(debug=True)