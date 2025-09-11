import datetime

from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


ACTIVITY_KEYS = [
    "run_id",
    "name",
    "start_date",
    "elapsed_time",
    "count",
    "avg_time",
    "calories",
]


class Activity(Base):
    __tablename__ = "activities"

    run_id = Column(Integer, primary_key=True)
    name = Column(String)
    start_date = Column(String)
    elapsed_time = Column(Integer)
    count = Column(Integer)
    avg_time = Column(Float)
    calories = Column(Float)

    def to_dict(self):
        out = {}
        for key in ACTIVITY_KEYS:
            attr = getattr(self, key)
            if isinstance(attr, (datetime.timedelta, datetime.datetime)):
                out[key] = str(attr)
            else:
                out[key] = attr
        return out


def update_or_create_activity(
    session, run_activity, count=0, avg_time=0.0, calories=0.0
):
    created = False
    try:
        activity = (
            session.query(Activity).filter_by(run_id=int(run_activity.id)).first()
        )

        if not activity:
            activity = Activity(
                run_id=run_activity.id,
                name=run_activity.name,
                elapsed_time=run_activity.elapsed_time,
                start_date=str(run_activity.start_date),
                count=count,
                avg_time=avg_time,
                calories=calories,
            )
            session.add(activity)
            created = True
        else:
            activity.name = run_activity.name
            activity.count = count
            activity.avg_time = avg_time
            activity.calories = calories
    except Exception as e:
        print(f"something wrong with {run_activity.id}")
        print(str(e))
        session.rollback()

    return created


def add_missing_columns(engine, model):
    inspector = inspect(engine)
    table_name = model.__tablename__
    columns = {col["name"] for col in inspector.get_columns(table_name)}
    missing_columns = []

    for column in model.__table__.columns:
        if column.name not in columns:
            missing_columns.append(column)
    if missing_columns:
        print(f"Adding missing columns {missing_columns} to {table_name}")
        with engine.connect() as conn:
            for column in missing_columns:
                column_type = str(column.type)
                conn.execute(
                    text(
                        f"ALTER TABLE {table_name} ADD COLUMN {column.name} {column_type}"
                    )
                )
            conn.commit()


def init_db(db_path):
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)

    # check missing columns
    add_missing_columns(engine, Activity)

    sm = sessionmaker(bind=engine)
    session = sm()
    # apply the changes
    session.commit()
    return session
