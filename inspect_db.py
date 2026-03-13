from app import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    db.create_all()
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tables in DB: {tables}")
    
    if 'follow' in tables:
        print("SUCCESS: 'follow' table exists.")
    else:
        print("ERROR: 'follow' table STILL missing.")
