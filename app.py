from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, World! This will be a URL Shortener soon."

if __name__ == "__main__":
    app.run(debug=True)
