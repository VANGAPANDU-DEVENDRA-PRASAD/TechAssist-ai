# Electronics Assistant

A Flask-based learning assistant for Electronics, Arduino & IoT, and Computer Software.

## Run locally

1. Create a virtual environment if you want to keep the project isolated.
2. Install the packages with `python -m pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and add your Groq API key.
4. Start with `python app.py` or double-click `start.bat`.
5. Open `http://127.0.0.1:5000`.

The Groq key is used only by the Flask backend. Do not commit `.env` to a public repository.

## Main folders

- `app.py` - Flask routes and API endpoints
- `advanced_bot.py` - Basic Mode search, calculations and Advanced Mode AI requests
- `data/` - knowledge base and project data
- `templates/` - page templates and the shared chatbot
- `static/` - CSS and browser-side JavaScript
