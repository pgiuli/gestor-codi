import sqlite3

def create_database():
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    # Create table for task submissions
    c.execute('''CREATE TABLE IF NOT EXISTS trameses
        (user text, taskid text, response blob, score text)''')
    # Create table for available tasks
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
        (taskid text, name text, open integer, description text)''')
    # Create table for users
    c.execute('''CREATE TABLE IF NOT EXISTS users
        (user text, password text, displayname text, role text)''')
    # Create table for documents
    c.execute('''CREATE TABLE IF NOT EXISTS documents
        (docid text, name text, document blob, extension text)''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user=?', (user_id,))
    user_info = c.fetchone()
    conn.close()
    return user_info

def get_task(task_id):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE taskid=?', (task_id,))
    task_info = c.fetchone()
    conn.close()
    return task_info

def save_response(user_id, task_id, response, score):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    if get_submission(user_id, task_id):
        c.execute('UPDATE trameses SET response=?, score=? WHERE user=? AND taskid=?', (response, score, user_id, task_id))
    else:
        c.execute('INSERT INTO trameses VALUES (?, ?, ?, ?)', (user_id, task_id, response, score))
    conn.commit()
    conn.close()

def get_submission(user_id, task_id):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('SELECT * FROM trameses WHERE user=? AND taskid=?', (user_id, task_id))
    submission = c.fetchone()
    conn.close()
    return submission

def grade_submission(user_id, task_id, score):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('UPDATE trameses SET score=? WHERE user=? AND taskid=?', (score, user_id, task_id))
    conn.commit()
    conn.close()

def get_grades(user_id):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('SELECT * FROM trameses WHERE user=?', (user_id,))
    grades = c.fetchall()
    conn.close()
    return grades

def get_grade(user_id, task_id):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('SELECT * FROM trameses WHERE user=? AND taskid=?', (user_id, task_id))
    grade = c.fetchone()
    conn.close()
    return grade

def get_submitted_tasks(user_id):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('SELECT taskid FROM trameses WHERE user=?', (user_id,))
    tasks = c.fetchall()
    conn.close()
    return tasks

def delete_submission(user_id, task_id):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('DELETE FROM trameses WHERE user=? AND taskid=?', (user_id, task_id))
    conn.commit()
    conn.close()

def get_tasks():
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    tasks = c.fetchall()
    conn.close()
    return tasks

def add_task(task_id, name, open, description):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('INSERT INTO tasks VALUES (?, ?, ?, ?)', (task_id, name, open, description))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE taskid=?', (task_id,))
    conn.commit()
    conn.close()

def update_task(task_id, name, open, description):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET name=?, open=?, description=? WHERE taskid=?', (name, open, description, task_id))
    conn.commit()
    conn.close()

def get_users():
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()
    return users

def add_user(user_id, password, displayname, role):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (user_id, password, displayname, role))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE user=?', (user_id,))
    conn.commit()
    conn.close()

def delete_user_submissions(user_id):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('DELETE FROM trameses WHERE user=?', (user_id,))
    conn.commit()
    conn.close()

def get_submissions_without_data():
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('SELECT user, taskid, score FROM trameses')
    submissions = c.fetchall()
    conn.close()
    return submissions

def get_user_submissions(user_id):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('SELECT taskid, score FROM trameses WHERE user=?', (user_id,))
    submissions = c.fetchall()
    conn.close()
    return submissions

def get_submission(user_id, task_id):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('SELECT * FROM trameses WHERE user=? AND taskid=?', (user_id, task_id))
    submission = c.fetchone()
    conn.close()
    return submission

def add_document(doc_id, name, document, extension):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('INSERT INTO documents VALUES (?, ?, ?, ?)', (doc_id, name, document, extension))
    conn.commit()
    conn.close()

def get_document(doc_id):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('SELECT * FROM documents WHERE docid=?', (doc_id,))
    document = c.fetchone()
    conn.close()
    return document

def get_documents_without_data():
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('SELECT docid, name FROM documents')
    documents = c.fetchall()
    conn.close()
    return documents

def delete_document(doc_id):
    conn = sqlite3.connect('trameses.db')
    c = conn.cursor()
    c.execute('DELETE FROM documents WHERE docid=?', (doc_id,))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_database()
    add_user('deleteme', 'admin', 'Administrator', '1')