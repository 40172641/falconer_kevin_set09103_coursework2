from flask import Flask, g
import sqlite3

from datetime import datetime

from flask import Flask, redirect, url_for, render_template
app = Flask(__name__)
db_location = 'static/test.db'

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
        timestamp = datetime.now().strftime('%Y-%M-%D %H:%M:%S')
        print timestamp
        #db.cursor().execute('DELETE FROM clothing')
        #db.cursor().execute('INSERT INTO clothing VALUES(2000,"Champion","T-Shirt", 37.99, %s)'(timestamp))
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

@app.route('/login/')
def login():
  return render_template("login.html")

@app.route('/register/')
def register():
  return render_tempalte("register.html")

#Error Handler
@app.errorhandler(404)
def page_not_found(error):
  return render_template('error.html'),404

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
