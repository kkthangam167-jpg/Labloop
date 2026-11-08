"""
run.py
──────
Entry point for the LabLoop Flask development server.

Usage
-----
    python run.py

For production, use gunicorn instead:
    gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
