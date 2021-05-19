import json

from sqlalchemy import Column, Integer, Date, String, Boolean, JSON


class StockPrice:
    """
    The class is used for ORM operations with price entries.
    """
    __tablename__ = 'stocks_prices'
    id = Column(String, primary_key=True)
    company_name = Column(String)
    price = Column(Integer)
    date = Column(Date)
    keys = ["company_name", "price", "date"]

    def __init__(self, _id, company_name, price, date):
        self.company_name = company_name
        self.price = price
        self.date = date
        self.id = _id

    def get_dict(self):
        return {"id": self.id, "price": self.price, "date": str(self.date), "company_name": self.company_name}

    def __repr__(self):
        return json.dumps(self.get_dict())


class Transaction:
    """
    The class is used for ORM operations with transaction entries.
    """
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    company_name = Column(String)
    number = Column(Integer)
    operation_type = Column(Boolean)
    date = Column(Date)
    keys = ["company_name", "number", "date", "operation_type"]

    def __init__(self, _id, company_name, number, operation_type, date):
        self.company_name = company_name
        self.number = number
        self.date = date
        self.operation_type = operation_type
        self.id = _id

    def get_dict(self):
        return {"id": self.id, "number": self.number, "company_name": self.company_name, "date": str(self.date),
                "operation_type": {True: "buy", False: "sell"}[self.operation_type]}

    def __repr__(self):
        return json.dumps(self.get_dict())


class State:
    """
    The class is used for ORM operations with state entries.
    """
    __tablename__ = 'states'
    id = Column(Integer)
    portfolio_state = Column(JSON)
    money = Column(Integer)
    date = Column(Date)

    keys = ["money", "portfolio_state", "date"]

    def __init__(self, portfolio_state=None, money=None, date=None):
        self.date = date
        self.portfolio_state = portfolio_state
        self.money = money

    def get_dict(self):
        return {"portfolio_state": self.portfolio_state, "money": self.money}

    def __repr__(self):
        return json.dumps(self.get_dict())


class User:
    """
    The class is used for ORM operations with user entries.
    """
    __tablename__ = 'accs'
    id = Column(Integer)
    user = Column(String)
    password = Column(String)

    def __init__(self, user=None, password=None):
        self.user = user
        self.password = password




