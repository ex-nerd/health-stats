
import os
import sqlite3
import re
from datetime import datetime

from pretty import pprint

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import Base
from models.events import *

Engine = create_engine(
    'sqlite:///'+os.path.expanduser("~/.health_stats/db.sqlite3"),
    # echo=True,  # Enable to see log statements
)

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(Engine)

Base.metadata.bind = Engine
DBSession = sessionmaker(bind=Engine, autoflush=False)
