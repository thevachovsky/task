import copy
import datetime
import uuid

from dateutil.relativedelta import relativedelta
from sqlalchemy import Table, Column, Integer, Date, String, MetaData, create_engine, Boolean, JSON, desc
from sqlalchemy.orm import mapper, sessionmaker

from settings import Settings
from sqlconnector.models import Transaction, StockPrice, State, User


class SQLSession:
    '''
    The class implements high-level access to system's database.
    '''
    def __init__(self):
        self.session = sessionmaker(bind=SQLConnector.engine)()

    def __enter__(self):
        return self.session

    def __exit__(self, *args, **kwargs):
        self.session.commit()
        self.session.close()


class SQLConnector:
    settings = Settings.get_settings()
    metadata = MetaData()
    prices_table = Table("stocks_prices", metadata,
                         Column("id", String, primary_key=True), Column("company_name", String),
                         Column("price", Integer), Column("date", Date))
    transactions = Table("transactions", metadata,
                         Column("id", String, primary_key=True), Column("company_name", String),
                         Column("number", Integer), Column("operation_type", Boolean), Column("date", Date))
    states = Table("states", metadata,
                         Column("id", Integer, primary_key=True), Column("portfolio_state", JSON),
                         Column("money", Integer), Column("date", Date))
    accs = Table("accs", metadata,
                   Column("id", Integer, primary_key=True), Column("user", String),
                   Column("password", String))

    mapper(StockPrice, prices_table)
    mapper(Transaction, transactions)
    mapper(State, states)
    mapper(User, accs)

    engine = create_engine(settings.dbase_connection_settings, echo=True, pool_size=20)
    metadata.create_all(engine)

    @staticmethod
    def seed_users():
        '''
        The method creates initial credentials entries.
        :return:
        '''
        with SQLSession() as session:
            session.add(User(user="User", password="Password"))

    @staticmethod
    def check_user(user, password):
        '''
        The method checks whether requested user exists.
        :return:
        '''
        with SQLSession() as session:
            return session.query(User).filter(User.user == user).filter(User.password == password).first()

    @staticmethod
    def get_daily_prices(days=None):
        '''
        The method returns a list of Prices objects reflecting DB entries
        :param days: The period in past, expressed as a number of days before today.
        :return:
        '''
        with SQLSession() as session:
            return copy.deepcopy(
                session.query(StockPrice).filter(StockPrice.date >= SQLConnector.return_date_in_past(days)).all()
            )

    @staticmethod
    def post_daily_price(body):
        '''
        The method creates an entry reflecting a price for a certain company's stock prise, basing on body argument.
        :param body: A dictionary that includes parameters.
        It must include next ones: company_name(String), price(Integer), date(String with a datetime obj in isoformat).
        If date is not given, datetime.date obj for the current time is used.

        If price entry for the same date and company exists - patch method id used to update the existing one.
        :return:
        '''
        with SQLSession() as session:

            p_id = str(uuid.uuid4())
            date = body.get("date", datetime.datetime.now())
            date = datetime.datetime.fromisoformat(date) if isinstance(date, str) else date

            existing_entry = session.query(Transaction)\
                .filter(Transaction.date == date)\
                .filter(Transaction.company_name == body["company_name"])\
                .first()

            if existing_entry:
                SQLConnector.patch_daily_price(body=body, _id=existing_entry.id)
                return

            session.add(
                StockPrice(
                    company_name=body["company_name"], price=body["price"],
                    date=date, _id=p_id
                )
            )
            return p_id

    @staticmethod
    def patch_daily_price(body, _id):
        '''
        The method updates an entry reflecting a price for a certain company's stock prise basing on 'body' argument.
        :param body: A dictionary that includes parameters.
        It could include next ones: company_name(String), price(Integer), date(String with a datetime obj in isoformat).
        If date is not given, datetime.date obj for the current time is used.
        :param _id: ID of entry being updated.
        :return:
        '''
        with SQLSession() as session:
            price = session.query(StockPrice).filter(StockPrice.id == _id).first()
            for key in body:
                setattr(price, key, body[key])

    @staticmethod
    def get_transactions(days=None):
        '''
        The method returns a list of Transaction objects reflecting DB entries for Transactions.
        :param days: The period in past, expressed as a number of days before today.
        :return:
        '''
        with SQLSession() as session:
            return copy.deepcopy(
                session.query(Transaction).filter(Transaction.date >= SQLConnector.return_date_in_past(days)).all()
            )

    @staticmethod
    def post_transaction(body):
        '''
        The method creates an entry reflecting a transaction for a certain company's stock, basing on the body argument.
        :param body: A dictionary that includes parameters.
        It must include next ones: company_name(String), date(String with a datetime obj in isoformat),
        operation_type(Boolean one reflecting operation type: True for buying, False for selling), number(Integer).
        If date is not given, datetime.date obj for the current time is used.
        :return:
        '''
        with SQLSession() as session:
            t_id = str(uuid.uuid4())
            date = body.get("date", datetime.datetime.now())
            date = datetime.datetime.fromisoformat(date) if isinstance(date, str) else date
            session.add(
                Transaction(
                    _id=t_id, company_name=body["company_name"], number=body["number"],
                    operation_type=body["operation_type"], date=date
                )
            )
            return t_id

    @staticmethod
    def patch_transaction(body, _id):
        '''
          The method updates an entry reflecting a certain transaction basing on the body argument.
          :param body: A dictionary that includes parameters.
          It could include next ones: company_name(String), price(Integer), date(String with a datetime obj in isoformat).
          If date is not given, datetime.date obj for the current time is used.
          :param _id: ID of entry being updated.
          :return:
          '''
        with SQLSession() as session:
            price = session.query(Transaction).filter(Transaction.id == _id).first()
            for key in body:
                setattr(price, key, body[key])

    @staticmethod
    def get_last_state():
        '''
        The method returns the latest instance of State. It includes portfolio's state and current available money.
        :return:
        '''
        with SQLSession() as session:
            return copy.deepcopy(
                session.query(State).order_by(desc(State.date)).limit(1).first()
            )

    @staticmethod
    def get_year_states():
        '''
        The method returns a list State objects for a period of a year.
        :return:
        '''
        return SQLConnector.get_states()

    @staticmethod
    def get_states(days=None):
        '''
         The method returns a list State objects for a specified period in days. If 'days' argument isn't sent, a
         period of a year is used.
         :return:
         '''
        with SQLSession() as session:
            return copy.deepcopy(
                session.query(State).filter(State.date >= SQLConnector.return_date_in_past(days)).all()
            )


    @staticmethod
    def post_states(states):
        '''
        The method place a list of portfolio states
        :param states: A list of State objects from models.py module.
        '''
        states = [states] if isinstance(states, State) else states
        with SQLSession() as session:
            for state in states:
                session.add(state)

    @staticmethod
    def return_date_in_past(days=None):
        # Обычный объект datetime не поддерживает дельту по годам из-за високосного года.
        delta = datetime.timedelta(days=days) if days is not None else relativedelta(years=1)
        return datetime.datetime.now().date() - delta







