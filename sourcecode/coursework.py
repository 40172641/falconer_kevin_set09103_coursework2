from flask import Flask, g
import sqlite3
import random
import bcrypt
import os
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps

from datetime import datetime

from flask import Flask, redirect, url_for, render_template, request, session,json, flash, redirect
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

#Method which can be added to a route which requires the user to be logged in to view the page
def requires_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        status = session.get('logged_in', False)
        if not status:
            return redirect(url_for('.login'))
        return f(*args, **kwargs)
    return decorated

#Establishes database connection to the Foundation database which contains the clothing table
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

#Home page for the Website
@app.route('/')
def route():
        db = get_db()
        clothing = db.cursor().execute('SELECT * FROM clothing ORDER BY date DESC LIMIT 5')
        return render_template('home.html', clothing=clothing),200

#
@app.route('/brands/')
def brands():
    db=get_db()
    clothing = db.cursor().execute('SELECT DISTINCT brand FROM clothing ORDER BY brand')
    return render_template('brands.html', clothing=clothing)

#Renders template with all items from a specfic brand provided it matches a database entry
@app.route('/brands/<brand>/')
def brand(brand):
  db=get_db()
  clothing = db.cursor().execute('SELECT * FROM clothing WHERE brand=?',(brand,))
  return render_template('brand.html', clothing=clothing, id=id, brand=brand)

#Product Page
@app.route('/brands/<brand>/<id>')
def product(brand, id):
  db = get_db()
  brand_id = db.cursor().execute('SELECT * FROM clothing WHERE brand=? AND id=?',(brand, id))
  other_products = db.cursor().execute('SELECT * FROM clothing WHERE brand=?',(brand,))
  return render_template('product.html', clothing=brand_id, brands=brand,id=id)

#Renders template with all items in the website
@app.route('/clothing/')
def clothing():
  db = get_db()
  clothing = db.cursor().execute('SELECT * FROM clothing ORDER BY product_name')
  return render_template('clothing.html', clothing=clothing)

#Renders template based on the product_type variable
@app.route('/clothing/<product_type>/')
def product_type(product_type):
  db = get_db()
  product = db.cursor().execute('SELECT * FROM clothing WHERE product_type=?',(product_type,))
  return render_template('clothing.html', clothing=product)

@app.route('/clothing/products/')
def all_products():
  db = get_db()
  product = db.cursor().execute('SELECT DISTINCT product_type FROM clothing ORDER by product_type')
  return render_template('type.html', clothing=product)

#Returns template with latest addition to the Website/Webpage
@app.route('/latest/')
def latest():
  db = get_db()
  latest = db.cursor().execute('SELECT * FROM clothing ORDER BY date DESC LIMIT 10')
  return render_template('latest.html', clothing=latest)

#Logs out admin
@app.route('/logout/')
def logout():
    session['logged_in'] = False
    return redirect(url_for('.login'))

#Renders admin page
@app.route("/admin/")
@requires_login
def admin():
  return render_template("admin.html")

#Adds a new item to the Database and Website
@app.route("/admin/add-item/", methods=['POST', 'GET'])
@requires_login
def additem():
  db = get_db()
  if request.method == 'POST':
    id = random.randrange(1000,100000,2) #Generates Random number between 1000-100000 with a decimal of two
    image = request.files['datafile']
    image.save('static/img/%s.jpg' %id)
    brand = request.form['brand']
    product_type = request.form['product_type']
    price = request.form['price']
    colour = request.form['colour']
    product_name = request.form['product_name']
    date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    db.cursor().execute('INSERT INTO clothing VALUES(?,?,?,?,?,?,?)',(id, brand, product_name, product_type,colour, price, date))
    db.commit()
   # app.logger.info('New Item Added ? ? ? ?' (id, brand, product_type,product_name))
    return render_template('responseadd.html', id=id, brand=brand)
  else:
    return render_template('add.html')

#If the Admin inputs the correct ID number, then the item with that ID number will be updated with what is input in the forms
@app.route("/admin/amend-item/", methods=['POST', 'GET'])
@requires_login
def amenditem():
  db = get_db()
  if request.method == 'POST':
    id = request.form['id']
    image = request.files['datafile']
    image.save('static/img/%s.jpg' %id) #Saves the Image to Static Image folder, with the input ID
    brand_amend = request.form['brand']
    product_name_amend = request.form['product_name']
    product_type_amend = request.form['product_type']
    price_amend = request.form['price']
    colour_amend = request.form['colour']
    db.cursor().execute('UPDATE clothing SET brand=?, product_name=?, product_type=?, colour=?, price=?  WHERE id=?', (brand_amend, product_name_amend, product_type_amend, colour_amend, price_amend, id)) 
    db.commit()
    return render_template('responseAmend.html', id=id, brand=brand_amend)
  else:
    return render_template('amend.html')

#Renders webpage so that if the Admin inputs a correct ID Number, then the item will be removed
@app.route("/admin/remove-item/", methods=['POST', 'GET'])
@requires_login
def removeitem():
  db = get_db()
  if request.method == 'POST':
    id_delete = request.form['id']
    db.cursor().execute('DELETE FROM clothing WHERE id=(?)', (id_delete,))
    db.commit()
    return render_template('responseRemove.html')
  else:
    return render_template('remove.html')

@app.route("/admin/all/")
@requires_login
def all():
  db = get_db()
  all = db.cursor().execute('SELECT * FROM clothing ORDER BY product_name')
  return render_template('adminall.html', clothing=all)

#Lists all of the feedback from the contact us section
@app.route("/admin/messages/")
@requires_login
def messages():
  db = get_dbcontact()
  messages = db.cursor().execute('SELECT * FROM messages ORDER BY date DESC')
  db.commit()
  return render_template('messages.html', messages=messages)

#Login page, Will flash error if login is inccorect
@app.route("/login/", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = request.form['email']
        pw = request.form['password']
        if request.form['email'] !='admin':
          error = 'Invalid Credentials'
        else:
          if check_auth(request.form['email'], request.form['password']):
            session['logged_in'] = True
            flash('You were successfully signed in')
            return redirect(url_for('.admin'))
    return render_template('login.html', error=error)

@app.route("/contact/", methods=['POST', 'GET'])
def contact():
  db=get_dbcontact()
  if request.method == 'POST':
    print request.form
    names = request.form['name']
    email = request.form['email']
    message = request.form['message']
    timestamp = datetime.now().strftime('%d-%m-%Y %H:%M')#Get current time to be stored in date coloumn
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
  #logHandler = RotatingFileHandler('static/log/login.log', maxBytes=1000, backupCount=1)
  #logHandler.setLevel(logging.INFO)
  #app.logger.addHander(logHandler)
  app.run(host='0.0.0.0', debug=True)
