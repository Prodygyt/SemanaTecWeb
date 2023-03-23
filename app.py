from flask import Flask, render_template, request, redirect, url_for, session
# import firebase_admin
# from firebase_admin import credentials, auth
from functools import wraps
import traceback

app = Flask(__name__)
app.secret_key = 'secret_key'


config = {
  'apiKey': "AIzaSyDoZn0GZUPyO0X39Yduh0V1tXnz4b09DaY",
  'authDomain': "semanatecweb-43e74.firebaseapp.com",
  'projectId': "semanatecweb-43e74",
  'storageBucket': "semanatecweb-43e74.appspot.com",
  'messagingSenderId': "937328015280",
  'appId': "1:937328015280:web:880a747703050c88c1c875",
  'databaseURL': ""
}



# Decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            user_auth = auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            session['user_id'] = user_auth['localId']
            return redirect(url_for('dashboard'))
        except Exception:
            error = 'Invalid Credentials. Please try again.'
            traceback.print_exc()
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.create_user_with_email_and_password(email, password)
            session['user'] = email
            return redirect(url_for('dashboard'))
        except:
            error = 'Email already exists. Please use a different email.'
            return render_template('signup.html', error=error)

    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/summary')
@login_required
def summary():
    return render_template('summary.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
