from flask import Flask, g
import sqlite3
import random
import bcrypt
from functools import wraps

from datetime import datetime

from flask import Flask, redirect, url_for, render_template, request, session
app = Flask(__name__)
db_location = 'static/test.db'
app.secret_key = 'AOZr984753/3234/xyYR/!JER'

valid_email = 'admin'
valid_pwhash = bcrypt.hashpw('admin', bcrypt.gensalt())

def check_auth(email, password):
    if(email == valid_email and valid_pwhash == bcrypt.hashpw(password.encode('utf-8'), valid_pwhash)):
      return True
    return False

def requires_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        status = session.get('logged_in', False)
        if not status:
            return redirect(url_for('.route'))
        return f(*args, **kwargs)
    return decorated

def get_db():
  db = getattr(g, 'db', None)
  if db is None:
      db = sqlite3.connect(db_location)
      g.db = db
  return db

@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('static/schema.sql', mode='r') as f:
          db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def route():
        db = get_db()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        id = random.randrange(1000,100000,2)
        #db.cursor().execute('DELETE FROM clothing')
        #db.cursor().execute('INSERT INTO clothing VALUES(?,"Palace","T-Shirt", 36.99, ?)',(id, timestamp,))
        db.commit()
        clothing = db.cursor().execute('SELECT * FROM clothing ORDER BY date DESC LIMIT 5')
        return render_template('home.html', clothing=clothing)

@app.route('/brands/')
def brands():
    db=get_db()
    clothing = db.cursor().execute('SELECT DISTINCT brand FROM clothing ORDER BY brand')
    return render_template('brands.html', clothing=clothing)

@app.route('/brands/<brand>/')
def brand(brand):
  db=get_db()
  clothing = db.cursor().execute('SELECT * FROM clothing WHERE brand=?',(brand,))
  return render_template('brand.html', clothing=clothing)

@app.route('/logout/')
def logout():
    session['logged_in'] = False
    return redirect(url_for('.route'))

@app.route("/admin/")
@requires_login
def admin():
  return "Admin Page"

@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['email']
        pw = request.form['password']

        if check_auth(request.form['email'], request.form['password']):
          session['logged_in'] = True
          return redirect(url_for('.admin'))
    return render_template('login.html')

@app.route('/register/')
def register():
  return render_tempalte("register.html")

#Error Handler
@app.errorhandler(404)
def page_not_found(error):
  return render_template('error.html'),404

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
