# Workout Database
Our project designs a front-end to help gym members log, track, and analyze their workouts and nutrition. Members can manage their training routines, monitor progress, and search for trainers based on specialization and experience level.
```COMS4111Project1/
├── flaskr/                 
│   ├── static/             # Static files (CSS, JS, images, etc.)
│   ├── templates/          # HTML templates for the Flask app
│   ├── __init__.py         # Application factory
│   ├── auth.py             # Authentication module
│   ├── db.py               # Database connection/setup
│   ├── models/             # Group functionality-specific files
│   │   ├── equipment.py
│   │   ├── exercise.py
│   │   ├── location.py
│   │   ├── members.py
│   │   ├── nutrition.py
│   │   ├── progress.py
│   │   ├── trainer.py
│   │   ├── workout.py
│   └── schema.sql          # SQL schema
├── instance/               # Instance folder for sensitive configurations
│   └── app.db              # Example database file (if SQLite is used)
├── tests/                  # Add this folder for unit tests
│   ├── test_auth.py        # Example test for authentication
│   ├── test_exercise.py    # Example test for exercises
├── .gitignore              # Ignored files
├── requirements.txt        # Dependencies
├── README.md               # Project documentation```
