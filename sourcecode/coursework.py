from flask import Flask, redirect, url_for, render_template
app = Flask(__name__)

@app.route('/')
def route():
  return render_template('home.html')

#Error Handler
@app.errorhandler(404)
def page_not_found(error):
  return render_template('error.html'),404

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
