import os
from flask_migrate import Migrate
from app import create_app, db
from app.models import User
from flask import g

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "neo4j_db"):
        g.neo4j_db.close()
