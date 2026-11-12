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


## Configure Advanced Mode (Groq)

1. Create a Groq API key in your Groq account.
2. Copy `.env.example` to a file named `.env` in this project folder (the same folder as `app.py`).
3. Replace `YOUR_GROQ_API_KEY_HERE` with your actual key. Keep the key private and do not upload `.env` to GitHub.
4. Install dependencies with `pip install -r requirements.txt`.
5. Stop the Flask server and run `start.bat` again so the environment variable is loaded.

For Render or another hosting service, add `GROQ_API_KEY` and `GROQ_MODEL` in the service's Environment Variables settings, then redeploy/restart. A local `.env` file is not automatically uploaded to a hosting provider.

Basic Mode includes a NumPy entry in the bundled knowledge base.
