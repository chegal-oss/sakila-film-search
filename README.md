# Sakila Film Search

CLI application for searching films in the `sakila` database with filters by category, release period, and title.

## Requirements

- Python 3.14
- access to MySQL
- access to MongoDB

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Configuration

The project reads environment variables from the `.env` file.

Minimum required variables:

```env
DB_HOST=ich-db.edu.itcareerhub.de
DB_PORT=3306
DB_NAME=sakila
DB_USER=ich1
DB_PASSWORD=password
MONGO_URI=mongodb://user:password@host/?readPreference=primary&ssl=false&authMechanism=DEFAULT&authSource=db
MONGO_DATABASE=ich_edit
MONGO_COLLECTION=final_project_121225ptm_serg
```

## Run

```bash
source .venv/bin/activate
python3 main.py
```

## Features

- shows film categories
- shows release periods
- allows searching by film title
- displays paginated results
- supports search history storage in MongoDB
