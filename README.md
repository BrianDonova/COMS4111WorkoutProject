# Workout Database
Our project designs a front-end to help gym members log, track, and analyze their workouts and nutrition. Members can manage their training routines, monitor progress, and search for trainers based on specialization and experience level.

The database can be accessed here['http://34.23.10.25:5000/'].

## Consolidated Repo Structure
```COMS4111Project1/
├── flaskr/                 
│   ├── static/             # Static files (CSS, JS, images, etc.)
│   ├── templates/          # HTML templates for the Flask app
│   ├── __init__.py         # Application factory
│   ├── auth.py             # Authentication module
│   ├── db.py               # Database connection/setup
│   ├── pages/              # front-end pages               
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
├── .gitignore              # Ignored files
├── README.md               # Project documentation
```
