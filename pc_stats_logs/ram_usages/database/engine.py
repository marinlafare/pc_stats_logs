
# database/engine.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from urllib.parse import urlparse
import asyncpg
import asyncio


from database.models import Base

async_engine = None
AsyncDBSession = sessionmaker(expire_on_commit=False, class_=AsyncSession)

async def init_db(connection_string: str):
    """
    Initializes the asynchronous SQLAlchemy database engine and ensures
    the database and all mapped tables exist.
    """
    global async_engine

    print(f"DEBUG: init_db called with connection_string: {connection_string}") # Debug print

    parsed_url = urlparse(connection_string)
    db_user = parsed_url.username
    db_password = parsed_url.password
    db_host = parsed_url.hostname
    db_port = parsed_url.port if parsed_url.port else 5432
    db_name = parsed_url.path.lstrip('/')

    print(f"DEBUG: Parsed DB details - Host: {db_host}, Port: {db_port}, User: {db_user}, DB Name: {db_name}") # Debug print

    temp_conn = None
    try:
        print(f"DEBUG: Attempting initial asyncpg.connect to 'postgres' database on {db_host}:{db_port}...") # Debug print
        temp_conn = await asyncpg.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database='postgres' # Connect to default 'postgres' DB to check/create your target DB
        )
        print("DEBUG: Successfully connected to 'postgres' database.") # Debug print

        db_exists_query = f"SELECT 1 FROM pg_database WHERE datname='{db_name}'"
        print(f"DEBUG: Checking if database '{db_name}' exists...") # Debug print
        db_exists = await temp_conn.fetchval(db_exists_query)

        if not db_exists:
            print(f"Database '{db_name}' does not exist. Creating...")
            await temp_conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database '{db_name}' created.")
        else:
            print(f"Database '{db_name}' already exists.")

    except asyncpg.exceptions.DuplicateDatabaseError:
        print(f"Database '{db_name}' already exists (concurrent creation attempt).")
    except Exception as e:
        print(f"DEBUG: Error during initial database existence check/creation: {e}") # Debug print
        # import traceback
        # traceback.print_exc() # Uncomment for full traceback if needed
        raise # Re-raise the exception to ensure it's visible in the logs
    finally:
        if temp_conn:
            print("DEBUG: Closing temporary connection to 'postgres' database.") # Debug print
            await temp_conn.close()

    # Ensure connection_string uses 'postgresql+asyncpg' for SQLAlchemy
    if not connection_string.startswith("postgresql+asyncpg://"):
        print("DEBUG: Adjusting connection string to use 'postgresql+asyncpg'...") # Debug print
        connection_string = connection_string.replace("postgresql://", "postgresql+asyncpg://", 1)

    print(f"DEBUG: Creating SQLAlchemy async engine with final connection string: {connection_string}") # Debug print
    async_engine = create_async_engine(connection_string, echo=False) # echo=True for SQL logging

    print("DEBUG: Beginning transaction to ensure database tables exist...") # Debug print
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("DEBUG: Database tables checked/created.") # Debug print

    AsyncDBSession.configure(bind=async_engine)
    print("DEBUG: Asynchronous database initialization complete.") # Debug print
