CREATE TABLE Member(
	member_id int, 
	name text,
	email_address text, 
	age int, 
	gender text, 
	height int, 
	weight int,
	PRIMARY KEY (member_id)
);
CREATE TABLE Trainer(
    trainer_id SERIAL PRIMARY KEY, 
    experience_level TEXT NOT NULL,
    certifications TEXT, 
    specialization TEXT
);
CREATE TABLE Workout(
    workout_id SERIAL PRIMARY KEY, 
    name TEXT NOT NULL, 
    duration FLOAT, 
    difficulty_level INT
);
CREATE TABLE Nutrition(
    nutrition_id SERIAL PRIMARY KEY, 
    name TEXT NOT NULL, 
    calories INT NOT NULL, 
    proteins INT NOT NULL, 
    carbohydrates INT NOT NULL, 
    created_at DATE DEFAULT CURRENT_DATE
);
CREATE TABLE Progress(
    progress_id SERIAL PRIMARY KEY, 
    progress_photos_url TEXT, 
    weekly_summary TEXT, 
    created_at DATE DEFAULT CURRENT_DATE
);
CREATE TABLE Exercises(
    exercise_id SERIAL, 
    workout_id INT NOT NULL REFERENCES Workout(workout_id), 
    name TEXT NOT NULL, 
    description TEXT, 
    reps INT, 
    sets INT, 
    duration FLOAT, 
    PRIMARY KEY (exercise_id, workout_id)
);
CREATE TABLE Location(
    location_id SERIAL PRIMARY KEY, 
    amenities TEXT, 
    capacity INT
);
CREATE TABLE Equipment(
    equipment_id SERIAL PRIMARY KEY, 
    name TEXT NOT NULL, 
    type TEXT NOT NULL
);
CREATE TABLE Coaches(
    member_id INT NOT NULL UNIQUE REFERENCES Member(member_id), 
    trainer_id INT NOT NULL REFERENCES Trainer(trainer_id), 
    PRIMARY KEY (member_id)
);
CREATE TABLE Tracks(
    member_id INT NOT NULL, 
    nutrition_id INT NOT NULL, 
    PRIMARY KEY (member_id, nutrition_id), 
    FOREIGN KEY (member_id) REFERENCES Member(member_id), 
    FOREIGN KEY (nutrition_id) REFERENCES Nutrition(nutrition_id)
);
CREATE TABLE Completes(
    member_id INT NOT NULL, 
    workout_id INT NOT NULL, 
    PRIMARY KEY (member_id, workout_id), 
    FOREIGN KEY (member_id) REFERENCES Member(member_id), 
    FOREIGN KEY (workout_id) REFERENCES Workout(workout_id)
);
CREATE TABLE Creates(
    member_id INT NOT NULL, 
    progress_id INT NOT NULL, 
    PRIMARY KEY (member_id, progress_id), 
    FOREIGN KEY (member_id) REFERENCES Member(member_id), 
    FOREIGN KEY (progress_id) REFERENCES Progress(progress_id)
);
CREATE TABLE Stored(
    workout_id INT NOT NULL UNIQUE REFERENCES Workout(workout_id), 
    progress_id INT NOT NULL REFERENCES Progress(progress_id), 
    PRIMARY KEY (workout_id)
);
CREATE TABLE Contains( 
    exercise_id INT NOT NULL UNIQUE, 
    workout_id INT NOT NULL REFERENCES Workout(workout_id) ON DELETE CASCADE, 
    PRIMARY KEY (exercise_id)
);
CREATE TABLE Occur( 
    exercise_id INT NOT NULL, 
    location_id INT NOT NULL REFERENCES Location(location_id) ON DELETE NO ACTION, 
    PRIMARY KEY (exercise_id, location_id)
);
CREATE TABLE Requires( 
    exercise_id INT NOT NULL, 
    equipment_id INT NOT NULL REFERENCES Equipment(equipment_id) ON DELETE NO ACTION, 
    PRIMARY KEY (exercise_id, equipment_id)
);
