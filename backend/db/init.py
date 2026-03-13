from models.task import Base
from db.session import engine
from sqlalchemy import inspect


def create_db_and_tables():
    """
    Create database tables or add missing columns.
    """
    # Check if tables exist
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # Create all tables at once using the shared Base metadata
    Base.metadata.create_all(bind=engine)

    # If tasks table exists, check if it has the priority column
    if 'tasks' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('tasks')]
        if 'priority' not in columns:
            # Add the priority column to the existing table
            from sqlalchemy import text
            with engine.connect() as conn:
                # Add priority column with default value
                conn.execute(text("ALTER TABLE tasks ADD COLUMN priority VARCHAR(50) DEFAULT 'medium';"))
                conn.commit()
                print("Added 'priority' column to tasks table")

    if 'tasks' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('tasks')]
        if 'last_modified_by' not in columns:
            # Add the last_modified_by column to the existing table
            from sqlalchemy import text
            with engine.connect() as conn:
                # Add last_modified_by column
                conn.execute(text("ALTER TABLE tasks ADD COLUMN last_modified_by VARCHAR(255);"))
                conn.commit()
                print("Added 'last_modified_by' column to tasks table")
                
    if 'tasks' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('tasks')]
        if 'due_date' not in columns:
            # Add the due_date column to the existing table
            from sqlalchemy import text
            with engine.connect() as conn:
                # Add due_date column
                conn.execute(text("ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE;"))
                conn.commit()
                print("Added 'due_date' column to tasks table")