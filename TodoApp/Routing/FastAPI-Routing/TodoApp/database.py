from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def get_engine(type="postgresql"):
    engine = None
    if type == "postgresql":
      SQLALCHEMY_DATABASE_URL_POSTGRESQL = \
        "postgresql://postgres:trantor@localhost/TodoApplicationDatabase"  # postgresql url

      engine = create_engine(
          SQLALCHEMY_DATABASE_URL_POSTGRESQL
      )
    elif type == "sqlite":
      SQLALCHEMY_DATABASE_URL_SQLITE = \
        "sqlite:///./todos.db"

      engine = create_engine(
          SQLALCHEMY_DATABASE_URL_SQLITE,
          connect_args={"check_same_thread": False}
      )
    elif type == "mysql":
      SQLALCHEMY_DATABASE_URL_MYSQL = \
        "mysql+pymysql://root:Trantor#1@127.0.0.1:3306/todo_application_database"  # mysql url

      engine = create_engine(
          SQLALCHEMY_DATABASE_URL_MYSQL
      )
    elif type == "mariadb":
      SQLALCHEMY_DATABASE_URL_MARIADB = \
        "mysql+pymysql://root:trantor@127.0.0.1:12354/todoapp"  # mariadb url

      engine = create_engine(
          SQLALCHEMY_DATABASE_URL_MARIADB
      )
    else:
      raise Exception("Invalid database type")
    
    return engine

engine = get_engine(type="mariadb")
if engine is not None:
  SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  Base = declarative_base()
else:
  raise Exception("Invalid database type")
