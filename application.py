from flask import Flask, request, render_template, redirect, url_for, session, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
from estimation_calculation import cal_effort_and_confidence_level

app = Flask(__name__)
connection = MongoClient('mongodb://localhost:27017/')
db = connection['the_effort_estimation']
user_data = db['users']
task_data = db['tasks']
app.secret_key = 'ad9867b5b78e87a0c17291c6c33d4e75f0a43d202b5ba801c7aed0dcc3de1fad'



# Home Page
@app.route('/')
def home():
    return render_template('/home.html')

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        hash_password = generate_password_hash(password)

        if user_data.find_one({'email':email}) or user_data.find_one({'username':username}):
            return render_template('register.html', mes="Already registered user! Please log in.")
        
        user_data.insert_one({'username':username, 'email':email, 'password':hash_password})
        return redirect(url_for('login'))
    
    return render_template('register.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        existing_user = user_data.find_one({'email':email})
        if existing_user and check_password_hash(existing_user['password'], password):
            session['email'] = email  
            return redirect(url_for('estimation_submission'))
        else:
            return render_template('login.html', mes="Invalid email or password")
    return render_template('login.html')

# login decorator
def login_required(func):
    @wraps(func)
    def inner():
        if 'email' not in session:
            flash('Please log in first!', 'error')
            return redirect(url_for('login'))
        return func()
    return inner

# show all tasks that are added into historical data
@login_required
@app.route('/show_estimation_submission')
def show_estimation_submission():
    # print("check")

    logged_user = user_data.find_one({'email':session['email']})
    if logged_user:
        all_tasks = task_data.find()
        # print(all_tasks)
        return render_template('show_estimation_submission.html', all_tasks=all_tasks)
    flash('User not found!', 'error')
    return redirect(url_for('login'))

# add tasks to historical data
@login_required
@app.route('/estimation_submission', methods=['GET', 'POST'])
def estimation_submission():
    logged_user = user_data.find_one({'email':session['email']})
    if logged_user:
        if request.method == 'POST':
            title = request.form['title']
            complexity = request.form['complexity']
            size = request.form['size']
            task_type = request.form['task_type']
            description = request.form['description']
            confidence_level, mean_estimated_effort, min_estimated_range, max_estimated_range = cal_effort_and_confidence_level(complexity, size)
            data = {'title':title, 'complexity':complexity, 'size':size, 'task_type':task_type, 
                    'description':description, 'confidence_level':confidence_level,
                     'mean_estimated_effort':mean_estimated_effort, 'min_estimated_range':min_estimated_range, 
                     'max_estimated_range':max_estimated_range}
            # print(data)
            task_data.insert_one(data)    
            return render_template("dashboard.html",task = data)
        return render_template("estimation_submission.html")
    flash('User not found!', 'error')
    return redirect(url_for('login'))

# Main Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    logged_user = user_data.find_one({'email':session['email']})
    if logged_user:
        username = logged_user['username']
        return render_template('dashboard.html', username=username)
    flash('User not found!', 'error')
    return redirect(url_for('login'))

# remove tasks from historical data
@app.route('/delete_task/<string:id>', methods=['POST'])
def remove_task(id):
    if request.method == 'POST':
        try:
            print(id)
            print(type(id))
            task_data.delete_one({'_id':ObjectId(id)})
            flash('Task deleted successfully', 'success')
            return redirect(url_for('show_estimation_submission'))
        except Exception as e:
            flash(f'Error deleting task: {str(e)}', 'error')
            return redirect(url_for('show_estimation_submission'))

# update existing tasks of historical data
@app.route('/update_task/<string:id>', methods=['GET','POST'])
def update_task(id):
    logged_user = user_data.find_one({'email': session['email']})
    if logged_user:
        if request.method == 'POST':
            title = request.form['title']
            complexity = request.form['complexity']
            size = request.form['size']
            task_type = request.form['task_type']
            description = request.form['description']
            confidence_level, mean_estimated_effort, min_estimated_range, max_estimated_range = cal_effort_and_confidence_level(complexity, size)
            data = {
                'title': title,
                'complexity': complexity,
                'size': size,
                'task_type': task_type,
                'description': description,
                'confidence_level': confidence_level,
                'mean_estimated_effort': mean_estimated_effort,
                'min_estimated_range': min_estimated_range,
                'max_estimated_range': max_estimated_range
            }
            try:
                task_data.update_one({'_id': ObjectId(id)}, {'$set': data})
                flash('Task updated successfully', 'success')
                return redirect(url_for('show_estimation_submission'))
            except Exception as e:
                flash(f'Error updating task: {str(e)}', 'error')
                return redirect(url_for('show_estimation_submission'))
        else:
            task = task_data.find_one({'_id': ObjectId(id)})
            if task:
                return render_template('update_data.html', task=task)
            else:
                flash('Task not found!', 'error')
                return redirect(url_for('show_estimation_submission'))
    flash('User not found!', 'error')
    return redirect(url_for('login')) 

# User Logout
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login')) 

if __name__ == '__main__':
    app.run(debug=True, port=5555)

