from flask import Flask, request, send_file, redirect, send_from_directory, render_template
from werkzeug.exceptions import RequestEntityTooLarge
from flask_login import current_user, UserMixin, LoginManager, login_required, login_user, logout_user
import db
import os
import dotenv
import tempfile
import zipfile

gestor = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(gestor)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    user_info = db.get_user(user_id)
    if user_info:
        return User(*user_info)
    return None

dotenv.load_dotenv()
gestor.secret_key = os.getenv('SECRET_KEY')

gestor.config['MAX_CONTENT_LENGTH'] = 64 * 1024

class User(UserMixin):
    def __init__(self, user_id, password, display_name, role):
        self.id = user_id
        self.password = password
        self.display_name = display_name
        self.role = role
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_admin(self):
        if self.role == '1':
            return True
        return False

@gestor.route('/')
def index():
    #If logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect('/dashboard')
    else:
        return redirect('/login')

@gestor.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try_user_id = request.form['user_id']
        try_password = request.form['password']
        user_info = db.get_user(try_user_id)
        if user_info:
            user = User(*user_info)
            if user.password == try_password:
                login_user(user)
                return redirect('/dashboard')
        available_users = db.get_users()
        return render_template('login.html', users=available_users,error='Credencials Errònies')
    if current_user.is_authenticated:
        return redirect('/dashboard')
    if request.method == 'GET':
        available_users = db.get_users()
        return render_template('login.html', users=available_users)


@gestor.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return render_template('admin_dashboard.html', current_user=current_user)
    else:
        return render_template('dashboard.html', current_user=current_user)
    
@gestor.route('/estat')
@login_required
def task_status():
    tasks = db.get_tasks()
    users = db.get_users()
    #Remove admin from users
    users = [user for user in users if user[3] != '1']
    average_grades = {}
    grading = {
        'NQ': 5,
        'NA': 0,
        'AS': 5,
        'AN': 7.5,
        'AE': 10
    }
    for user in users:
        avg = 0
        count = 0
        for task in tasks:
            submission = db.get_submission(user[0], task[0])
            if submission:
                avg += int(grading[submission[3]])
            count += 1
        avg /= count
        average_grades[user[0]] = avg
    user_submission_status = []
    for user in users:
        for task in tasks:
            submission = db.get_submission(user[0], task[0])
            if submission:
                user_submission_status.append((user[0], task[0], f'✅ - {submission[3]}'))
            else:
                user_submission_status.append((user[0], task[0], '❌'))
    return render_template('status.html', tasks=tasks, users=users, user_submission_status=user_submission_status, current_user=current_user, average_grades=average_grades, grading=grading)

@gestor.route('/consulta', methods=['GET', 'POST'])
@login_required
def query():
    if request.method == 'POST':
        task_id = request.form['task_id']
        user_id = request.form['user_id']
        #Hehe
        if user_id != current_user.id and not current_user.is_admin:
            return render_template('query.html', error="Només pots consultar les teves trameses", current_user=current_user)
        submission = db.get_submission(user_id, task_id)

        if not submission:
            tasks = db.get_tasks()
            return render_template('query.html', tasks=tasks, error="No s'ha trobat cap tramesa", current_user=current_user)

        else:
            temp = tempfile.NamedTemporaryFile(mode='wb', delete=False)
            temp.write(submission[2])
            temp.close()
            return send_file(temp.name, as_attachment=True, download_name=f'{user_id}_{task_id}.py')
    else:
        if current_user.is_admin:
            tasks = db.get_tasks()
            users = db.get_users()
            users = [user for user in users if user[3] != '1']
            return render_template('query.html', tasks=tasks, users=users, current_user=current_user)
        else:
            tasks = db.get_tasks()
            return render_template('query.html', tasks=tasks, current_user=current_user)

@gestor.route('/enviament', methods=['GET', 'POST'])
@login_required
def submission():
    if request.method == 'POST':
        file = request.files['file']
        print(f"{current_user.id} is submitting {request.form['task_id']}")
        if not file:
            return render_template('submit.html', error="No s\'ha seleccionat cap arxiu", current_user=current_user)
        if db.get_task(request.form['task_id'])[2] == 0:
            return render_template('submit.html', error="La tasca està tancada", current_user=current_user, tasks=db.get_tasks())
        db.save_response(current_user.id, request.form['task_id'], file.read(), 'NQ')
        return redirect('/enviament')
    else:
        tasks = db.get_tasks()
        return render_template('submit.html', tasks=tasks, current_user=current_user)

@gestor.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@gestor.route('/descarrega')
@login_required
def download():
    if not current_user.is_admin:
        return redirect('/dashboard')
    with tempfile.TemporaryDirectory() as tempdir:
        submissions = db.get_submissions_without_data()
        for submission in submissions:
            user_id = submission[0]
            task_id = submission[1]
            submission_data = db.get_submission(user_id, task_id)
            task_dir = os.path.join(tempdir, str(task_id))
            os.makedirs(task_dir, exist_ok=True)
            with open(f'{task_dir}/{user_id}.py', 'wb') as f:
                f.write(submission_data[2])

        with zipfile.ZipFile('submissions.zip', 'w') as zipf:
            for root, dirs, files in os.walk(tempdir):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), tempdir))
    return send_file('submissions.zip', as_attachment=True)

@gestor.route('/puntua', methods=['POST', 'GET'])
@login_required
def grade():
    if not current_user.is_admin:
        return redirect('/dashboard')
    if request.method == 'POST':
        if current_user.is_admin:
            db.grade_submission(request.form['user_id'], request.form['task_id'], request.form['grade'])
            return redirect('/puntua')
        else:
            return redirect('/dashboard')
    else:
        users = db.get_users()
        users = [user for user in users if user[3] != '1']
        tasks = db.get_tasks()
        return render_template('grade.html', users=users, tasks=tasks, current_user=current_user)

@gestor.route('/gestio', methods=['GET'])
@login_required
def manage():
    if not current_user.is_admin:
        return redirect('/dashboard')
    return render_template('manage.html', current_user=current_user)

@gestor.route('/tasques', methods=['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
        task_id = request.form['task_id']
        task = db.get_task(task_id)
        if task[2] == 1:
            db.update_task(task_id, task[1], 0, task[3])
        else:
            db.update_task(task_id, task[1], 1, task[3])
        return redirect('/tasques')
    tasks = db.get_tasks()
    return render_template('tasks.html', tasks=tasks, current_user=current_user)

@gestor.route('/add', methods=['POST', 'GET'])
@login_required
def add():
    if request.method == 'GET':
        return render_template('add.html', current_user=current_user)
    else:
        if not current_user.is_admin:
            return redirect('/dashboard')
        type = request.form['type']
        if type == 'task':
            task_id = request.form['task_id']
            task_name = request.form['task_name']
            description = request.form['description']
            if task_id in [task[0] for task in db.get_tasks()]:
                return render_template('add.html', error='Ja existeix una tasca amb aquest ID', current_user=current_user)
            db.add_task(task_id, task_name, description=description, open=1)
        elif type == 'user':
            user_id = request.form['user_id']
            password = request.form['password']
            display_name = request.form['display_name']
            role = request.form['role']
            print(user_id, password, display_name, role)
            if user_id in [user[0] for user in db.get_users()]:
                return render_template('add.html', error='Ja existeix un usuari amb aquest ID', current_user=current_user)
            db.add_user(user_id, password, display_name, role)
        elif type == 'document':
            print("a")
            print(request.form)
            doc_id = request.form['doc_id']
            doc_name = request.form['doc_name']
            document = request.files['document']
            extension = document.filename.split('.')[-1]
            if doc_id in [doc[0] for doc in db.get_documents_without_data()]:
                return render_template('add.html', error='Ja existeix un document amb aquest ID', current_user=current_user)
            db.add_document(doc_id, doc_name, document.read(), extension)
        return redirect('/add')

@gestor.route('/delete', methods=['POST', 'GET'])
@login_required
def delete():
    if request.method == 'GET':
        tasks = db.get_tasks()
        users = db.get_users()
        documents = db.get_documents_without_data()
        return render_template('delete.html', users=users, tasks=tasks, documents=documents, current_user=current_user)
    else:
        if not current_user.is_admin:
            return redirect('/dashboard')
        type = request.form['type']
        if type == 'task':
            task_id = request.form['task_id']
            db.delete_task(task_id)
        elif type == 'user':
            user_id = request.form['user_id']
            db.delete_user(user_id)
        elif type == 'document':
            doc_id = request.form['doc_id']
            db.delete_document(doc_id)
        return redirect('/delete')

@gestor.route('/documents')
@login_required
def documents():
    #Downloads the document if it's present in the arguments of the request
    if 'doc_id' in request.args:
        doc_id = request.args['doc_id']
        doc = db.get_document(doc_id)
        extension = doc[3]
        if doc:
            temp = tempfile.NamedTemporaryFile(mode='wb', delete=False)
            temp.write(doc[2])
            temp.close()
            return send_file(temp.name, as_attachment=True, download_name=f'{doc_id}.{extension}')
        return redirect('/documents')
    documents = db.get_documents_without_data()
    return render_template('documents.html', documents=documents, current_user=current_user)

@gestor.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(gestor.root_path, 'static'), 'favicon.ico')

@gestor.errorhandler(404)
def page_not_found(e):
    #print(f"{current_user.id} is trying to access a non-existent page: {request.path}")
    return redirect('/')

@gestor.errorhandler(RequestEntityTooLarge)
def handle_file_size_exceeded(e):
    return redirect('https://youtu.be/dQw4w9WgXcQ')

if __name__ == '__main__':
    gestor.run(debug=True)