from flask import Flask, g
import sqlite3
import random
import bcrypt
import os
from functools import wraps

from datetime import datetime
#from flask.ext.uploads import UploadSet, configure_uploads, IMAGES

#photos = UploadSet('photos', IMAGES)

from flask import Flask, redirect, url_for, render_template, request, session,json, flash

app = Flask(__name__)

db_location = 'static/foundation.db'
dbcontact_location ='static/contact.db'
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
            return redirect(url_for('.login'))
        return f(*args, **kwargs)
    return decorated

def get_db():
  db = getattr(g, 'db', None)
  if db is None:
      db = sqlite3.connect(db_location)
      g.db = db
  return db

def get_dbcontact():
  db_contact = getattr(g, 'db_contact', None)
  if db_contact is None:
    db_contact = sqlite3.connect(dbcontact_location)
    g.db_contact = db_contact
  return db_contact

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

def init_dbcontact():
    with app.app_context():
        db_contact = get_dbcontact()
        with app.open_resource('static/contact.sql', mode='r') as f:
          db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def route():
        db = get_db()
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
  return render_template('brand.html', clothing=clothing, id=id)

@app.route('/brands/<brand>/<id>')
def product(brand, id):
  db = get_db()
  json_file=open('static/foundation.json').read()
  brands=json.loads(json_file)
  clothing = db.cursor().execute('SELECT * FROM clothing WHERE brand=? AND id=?',(brand, id))
 # for brand in brands:
  #  if brand['id']==id:
  return render_template('product.html', clothing=clothing, brands=brand,id=id)

@app.route('/logout/')
def logout():
    session['logged_in'] = False
    return redirect(url_for('.login'))

@app.route("/admin/")
@requires_login
def admin():
  return render_template("admin.html")

@app.route("/admin/add-item/", methods=['POST', 'GET'])
@requires_login
def additem():
  db = get_db()
  if request.method == 'POST':
    id = random.randrange(1000,100000,2)
    print id
   # os.makedirs('static/img/%s' %id)
    image = request.files['datafile']
    image.save('static/img/%s.jpg' %id)
    print id
    brand = request.form['brand']
    product_type = request.form['product_type']
    price = request.form['price']
    colour = request.form['colour']
    product_name = request.form['product_name']
    date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    db.cursor().execute('INSERT INTO clothing VALUES(?,?,?,?,?,?,?)',(id, brand, product_name, product_type,colour, price, date))
    db.commit()
    return render_template('responseAmend.html', id=id, brand=brand)
  else:
    return render_template('add.html')

@app.route("/admin/amend-item/", methods=['POST', 'GET'])
@requires_login
def amenditem():
  db = get_db()
  if request.method == 'POST':
    id = request.form['id']
    image = request.files['datafile']
    image.save('static/img/%s.jpg' %id)
    brand_amend = request.form['brand']
    product_name_amend = request.form['product_name']
    product_type_amend = request.form['product_type']
    price_amend = request.form['price']
    colour_amend = request.form['colour']
    db.cursor().execute('UPDATE clothing SET brand=?, product_name=?, product_type=?, colour=?, price=?  WHERE id=?', (brand_amend, product_name_amend, product_type_amend, colour_amend, price_amend, id)) 
    db.commit()
    return "Amendment Successful"
  else:
    return render_template('amend.html')

@app.route("/admin/remove-item/", methods=['POST', 'GET'])
@requires_login
def removeitem():
  db = get_db()
  if request.method == 'POST':
    id_delete = request.form['id']
    db.cursor().execute('DELETE FROM clothing WHERE id=(?)', (id_delete,))
    db.commit()
    return "Item Removed"
  else:
    return render_template('remove.html')

@app.route("/admin/messages/")
@requires_login
def messages():
  db = get_dbcontact()
  messages = db.cursor().execute('SELECT * FROM messages ORDER BY date DESC')
  return render_template('messages.html', messages=messages)

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
  return render_template("register.html")

@app.route("/contact/", methods=['POST', 'GET'])
def contact():
  db=get_dbcontact()
  if request.method == 'POST':
    print request.form
    names = request.form['name']
    email = request.form['email']
    message = request.form['message']
    timestamp = datetime.now().strftime('%d-%m-%Y %H:%M')
    db.cursor().execute('INSERT INTO messages VALUES(?,?,?,?)',(names, email, message, timestamp))
    db.commit()
    return render_template('response.html', name=names)
  else:
    return render_template('contact.html')

#Error Handler
@app.errorhandler(404)
def page_not_found(error):
  return render_template('error.html'),404

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
