from sqlalchemy import create_engine
from sqlite_data_manager import Base, SQLiteDataManager

# Specify your database path
db_path = 'moviwebapp.db'

# Create the engine
engine = create_engine(f'sqlite:///{db_path}')

# Drop all tables (destructive)
Base.metadata.drop_all(engine)

# Recreate tables
Base.metadata.create_all(engine)

print("Database tables have been reset.")
