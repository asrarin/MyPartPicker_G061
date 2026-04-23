<<<<<<< HEAD
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Pc Part Picker"


if __name__ == "__main__":
=======
from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
>>>>>>> 717a1d73ff0f9b04c8166eb1af232afb821243ee
    app.run(debug=True)