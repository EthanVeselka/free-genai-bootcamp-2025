from invoke import task
from lib.db import db
import os
from pathlib import Path

@task
def init_db(c):
    """Initialize the database if it doesn't exist"""
    from flask import Flask
    app = Flask(__name__)
    db.init(app)
    print("Database initialized successfully.")

@task
def rm_db(c):
    """Remove the database file"""
    if Path('words.db').exists():
        os.remove('words.db')
        print("Database removed.")
    else:
        print("Database does not exist.")

@task
def reset_db(c):
    """Remove and reinitialize the database"""
    rm_db(c)
    init_db(c)
    print("Database reset complete.")