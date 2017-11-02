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
        date = datetime.now().strftime("%Y-%M-%d %H:%M:%S")
        #db.cursor().execute('DELETE FROM clothing')
      #  db.cursor().execute('INSERT INTO clothing VALUES(2000,"Champion","T-Shirt", 37.99, "2015")')
        db.commit()
        clothing = db.cursor().execute('SELECT * FROM clothing ORDER BY date DESC LIMIT 5')
        return render_template('home.html', clothing=clothing)

@app.route('/<brand>/')
def brands(brand):
    db=get_db()
    clothing = db.cursor().execute('SELECT brand FROM clothing')
    return render_template('brands.html', clothing=clothing)

@app.route('/<brand>/')
def brand(title):
  db=get_db()
  clothing = db.cursor().execute("""SELECT * FROM clothing WHERE title=?"""),(title)
  return render_template('brand.html', clothing=clothing)

#Error Handler
@app.errorhandler(404)
def page_not_found(error):
  return render_template('error.html'),404

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
