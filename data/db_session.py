"""
Everything required to work with SQLAlch database
"""
import sqlalchemy as sa
import sqlalchemy.orm as orm

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file):
    """Initialize a database

    :param db_file: database file name
    :return:
    """
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("No database file given")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Connecting a database: {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> orm.Session:
    """Make a [global_init]'s database session"""
    global __factory
    return __factory()
