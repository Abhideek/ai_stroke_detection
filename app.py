from flask import Flask, render_template, request, redirect, session,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
from OpenAI import openai
import os

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ------------------------------
# DATABASE CONFIG
# ------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///heart.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------------
# USER MODEL
# ------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))


# ------------------------------
# AUTO DB INITIALIZATION
# ------------------------------
with app.app_context():
    db.create_all()
    print("✔ Database initialized successfully!")


# ------------------------------
# LOAD MODEL + SCALER
# ------------------------------
model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")


# ------------------------------
# ROUTES
# ------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("signup.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect("/form")

        return "Invalid login details"

    return render_template("login.html")


# ---------- FORM ----------
@app.route("/form", methods=["GET", "POST"])
def form():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        # Collect patient inputs
        data = [
            float(request.form["age"]),
            float(request.form["gender"]),
            float(request.form["blood_pressure"]),
            float(request.form["cholesterol"]),
            float(request.form["max_hr"]),
            float(request.form["diabetes"])
        ]

        scaled = scaler.transform([data])
        prediction = model.predict(scaled)[0]

        result = "High Risk" if prediction == 1 else "Low Risk"

        return render_template("result.html", result=result)

    return render_template("form.html")


# ---------- CHATBOT PAGE ----------



# ---------- GPT CHAT API ----------
@app.route("/ask_gpt", methods=["POST"])
def ask_gpt():
    user_msg = request.json.get("message", "")

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a medical assistant chatbot."},
                {"role": "user", "content": user_msg}
            ]
        )

        reply = response.choices[0].message['content']

        return {"reply": reply}

    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

@app.route("/")
def index():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # Basic working AI reply (you can replace with GPT call later)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_message}]
        )
        ai_reply = response.choices[0].message["content"]
    except Exception:
        ai_reply = "Error: Could not connect to OpenAI."

    return jsonify({"reply": ai_reply})



# ------------------------------
# RUN APP
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
