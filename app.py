import json
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from advanced_bot import ask_groq, basic_answer, load_json, KNOWLEDGE_PATH, PROJECTS_PATH

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


def load_data(path, fallback):
    return load_json(path, fallback)


@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/electronics")
def electronics():
    return render_template("electronics.html")


@app.route("/arduino-iot")
def arduino_iot():
    return render_template("arduino_iot.html")


@app.route("/computer-software")
def computer_software():
    return render_template("computer_software.html")


@app.route("/learn")
def learn():
    return render_template("tools.html", active="learn", title="Learn Mode")


@app.route("/projects")
def projects():
    projects_data = load_data(PROJECTS_PATH, {"projects": []})
    return render_template("tools.html", active="projects", title="Projects", projects=projects_data.get("projects", []))


@app.route("/troubleshoot")
def troubleshoot():
    return render_template("tools.html", active="troubleshoot", title="Troubleshooting Lab")


@app.route("/calculator")
def calculator():
    return render_template("tools.html", active="calculator", title="ECE Calculator")




@app.route("/get", methods=["POST"])
def chatbot_reply():
    data = request.get_json(silent=True) or {}
    user_text = str(data.get("msg", ""))
    return jsonify({"reply": basic_answer(user_text), "mode": "basic"})


@app.route("/advanced_chat", methods=["POST"])
def advanced_chat():
    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()
    page_context = str(data.get("page_context", "")).strip()
    history = data.get("history") if isinstance(data.get("history"), list) else []
    try:
        result = ask_groq(user_message, page_context, history)
        return jsonify({"success": True, "answer": result, "mode": "advanced"})
    except Exception as exc:
        print("Groq API Error:", exc)
        return jsonify({
            "success": False,
            "answer": "Advanced AI could not complete that request. Please check the server API configuration or switch to Basic Mode.",
        }), 200


@app.route("/api/projects")
def api_projects():
    data = load_data(PROJECTS_PATH, {"projects": []})
    return jsonify(data)


@app.route("/api/knowledge")
def api_knowledge():
    data = load_data(KNOWLEDGE_PATH, {"knowledge": []})
    return jsonify({
        "name": data.get("name", "Electronics Assistant Knowledge Base"),
        "version": data.get("version", "1.0"),
        "count": len(data.get("knowledge", [])),
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
