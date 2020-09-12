import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from werkzeug.security import generate_password_hash, check_password_hash

from flaskr.database import Base, db_session as session


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_type = Column(String(50), nullable=False)
    pair = Column(String(50), nullable=False)

    buy_order_id = Column(Integer)
    buy_amount = Column(Float)
    buy_price = Column(Float)
    buy_created = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)
    buy_finished = Column(DateTime, nullable=True)
    buy_cancelled = Column(DateTime, nullable=True)
    buy_verified = Column(Boolean, default=False)

    sell_order_id = Column(Integer, nullable=True)
    sell_amount = Column(Float, nullable=True)
    sell_price = Column(Float, nullable=True)
    sell_created = Column(DateTime, nullable=True)
    sell_finished = Column(DateTime, nullable=True)
    force_sell = Column(Boolean, default=False)
    sell_verified = Column(Boolean, default=False)

    def __repr__(self):
        return f"({self.id}, {self.order_type}, {self.pair})"

    def is_sell(self):
        if self.order_type == 'sell':
            return True
        return False


class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, unique=True, nullable=True)
    description = Column(Text)
    order_type = Column(String(20), nullable=True)
    log_type = Column(String(20), nullable=True)
    price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=True)
    commission = Column(Float, nullable=True)
    fail = Column(Boolean, default=False)
    analysis_ = Column(Integer, nullable=True)
    create = Column(DateTime,  default=datetime.datetime.utcnow())

    def __repr__(self):
        return f"({self.id}, {self.fail})"

    @classmethod
    def create(cls, **kwargs):
        log = kwargs['log']
        if kwargs['log_type'] == 'info':
            log.info(kwargs['description'])
        elif kwargs['log_type'] == 'debug':
            log.debug(kwargs['description'])
        elif kwargs['log_type'] == 'warning':
            log.warning(kwargs['description'])
            kwargs['fail'] = True
        del kwargs['log']

        obj = cls(
            **kwargs
        )
        session.add(obj)
        session.commit()


class SettingValue(Base):
    __tablename__ = 'settingvalues'
    id = Column(Integer, primary_key=True)
    slug = Column(String(50)) # run / pause
    value = Column(String(50))

    def __repr__(self):
        return f"({self.id}, {self.slug}, {self.value})"


class PairSetting(Base):
    __tablename__ = 'pair_settings'
    id = Column(Integer, primary_key=True)
    base = Column(String(20))
    quote = Column(String(20))
    spend_sum = Column(Integer)
    profit_markup = Column(Float)
    use_stop_loss = Column(Boolean)
    stop_loss = Column(Float)
    active = Column(Boolean)

    def __repr__(self):
        return f"({self.id}, {self.base}, {self.quote})"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    password = Column(String(50))
    is_admin = Column(Boolean, default=False)

    def __repr__(self):
        return f"({self.id}, {self.name})"

    @classmethod
    def create(cls, name, password, is_admin):
        obj = cls(
            name=name,
            password=generate_password_hash(password),
            is_admin=is_admin
        )
        session.add(obj)
        session.commit()

    def check_password(self, password):
        return check_password_hash(self.password, password)
