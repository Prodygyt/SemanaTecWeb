from flask import Flask, render_template, request, redirect, url_for, session, jsonify
# import firebase_admin
# from firebase_admin import credentials, auth
from functools import wraps
import pyrebase
import traceback
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import pytz

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

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# Use the application default credentials.
cred = credentials.Certificate('semanatecweb-43e74-firebase-adminsdk-p7uuw-c01332062b.json')

firebase_admin.initialize_app(cred)
db = firestore.client()



# Create a list of tasks filtered by their status
def list_tasks_ToDo():
    lista_tareas = []
    docs = db.collection(u'tareas').where(u'id_usuario', u'==', session['user_id']).where(u'status', u'==', 'To Do').stream()
    for doc in docs:
        doc_data = doc.to_dict()
        name = doc_data['nombre_tarea']
        lista_tareas.append(name)

    return lista_tareas
    
def list_tasks_Doing():
    lista_tareas = []
    docs = db.collection(u'tareas').where(u'id_usuario', u'==', session['user_id']).where(u'status', u'==', 'Doing').stream()
    for doc in docs:
        doc_data = doc.to_dict()
        name = doc_data['nombre_tarea']
        lista_tareas.append(name)

    return lista_tareas

def list_tasks_Done():
    lista_tareas = []
    docs = db.collection(u'tareas').where(u'id_usuario', u'==', session['user_id']).where(u'status', u'==', 'Done').stream()
    for doc in docs:
        doc_data = doc.to_dict()
        name = doc_data['nombre_tarea']
        lista_tareas.append(name)

    return lista_tareas

def list_tasks_summary():
    lista_tareas = []
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    cst_now = utc_now.astimezone(pytz.timezone("America/Monterrey"))
    docs = db.collection(u'tareas').where(u'id_usuario', u'==', session['user_id']).where(u'fecha', u'==', cst_now).stream()
    for doc in docs:
        doc_data = doc.to_dict()
        name = doc_data['nombre_tarea']
        lista_tareas.append(name)
        
    return lista_tareas

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
    lista_tareas_ToDo = list_tasks_ToDo()
    lista_tareas_Doing = list_tasks_Doing()
    lista_tareas_Done = list_tasks_Done()
    return render_template('dashboard.html', ToDo=lista_tareas_ToDo, Doing=lista_tareas_Doing, Done=lista_tareas_Done)

@app.route('/summary')
@login_required
def summary():
    return render_template('summary.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Setting up the route for creating documents in Firestore
@app.route('/create_document', methods=['GET','POST'])
@login_required
def create_document():
    if(request.method == 'POST'):
        # Getting the data from the form
        user_id = session['user_id']
        name = request.form['name']
        date = request.form['date']
        status = request.form['status']

        # Creating a reference to the Firestore collection
        doc_ref = db.collection('tareas').document()

        # Adding the data to the Firestore document
        doc_ref.set({
            'nombre_tarea': name,
            'fecha': date,
            'status': status,
            'id_usuario': user_id
        })
        
        # Redirecting to the home page
        return redirect('/dashboard')
    
    return render_template('createTask.html')


# Setting up the route for updating documents in Firestore
@app.route('/update_document', methods=['GET','POST'])
@login_required
def update_document():
    if(request.method == 'POST'):
        # Getting the data from the form
        user_id = session['user_id']
        name = request.form['name']
        date = request.form['date']
        status = request.form['status']

        # Creating a reference to the Firestore document
        docs = db.collection(u'tareas').where(u'id_usuario', u'==', session['user_id']).stream()
        doc_ref = db.collection('tareas').document(docs.id)

        # Updating the data in the Firestore document
        doc_ref.update({
            'nombre_tarea': name,
            'fecha': date,
            'status': status,
            'id_usuario': user_id
        })

        # Redirecting to the home page
        return redirect('/dashboard')
    
    return render_template('updateTask.html')


if __name__ == '__main__':
    app.run(debug=True)
