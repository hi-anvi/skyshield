# 🌦️ SkyShield

SkyShield is a Flask-based weather application that allows users to search for weather information and view weather-related data through a web interface.

## How the Project Works

### `app.py`
The main Flask application.

Responsibilities:
- Creates and configures the Flask app
- Defines application routes
- Handles user requests
- Renders HTML templates
- Connects the frontend with weather data

### `get_weather.py`
Contains the logic for retrieving weather information from an external weather API.

Responsibilities:
- Sends API requests
- Processes weather responses
- Returns formatted weather data to the Flask app

### `helpers.py`
Utility functions used throughout the application.

Examples:
- Data formatting
- Validation helpers
- Common reusable functions

### `templates/`
Contains Jinja2 HTML templates rendered by Flask.

Examples:
- Homepage
- Weather results page
- Error pages

### `static/`
Stores frontend assets.

Examples:
- CSS stylesheets
- JavaScript files
- Images and icons

### `weather.db`
SQLite database used by the application to store weather-related information and application data.

---

# Running the Application

## 1. Clone the Repository

```bash
git clone https://github.com/hi-anvi/skyshield.git
cd skyshield
```

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Flask

### Windows (Command Prompt)

```bash
set FLASK_APP=app.py
```

### Windows (PowerShell)

```powershell
$env:FLASK_APP="app.py"
```

### Linux/macOS

```bash
export FLASK_APP=app.py
```

## 5. Run the Application

```bash
flask run
```

You should see output similar to:

```text
* Running on http://127.0.0.1:5000
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

### Optional: Enable Debug Mode

Windows:

```bash
set FLASK_DEBUG=1
```

Linux/macOS:

```bash
export FLASK_DEBUG=1
```

Then run:

```bash
flask run
```

The server will automatically reload whenever code changes are detected.

---

## Tech Stack

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript

## Author

Anvi

GitHub: https://github.com/hi-anvi
