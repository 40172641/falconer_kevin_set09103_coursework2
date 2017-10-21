from flask import Flask, redirect, url_for
app = Flask(__name__)

@app.route('/')
def route():
  return "CW2"

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
