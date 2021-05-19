import copy
import datetime

from common.firms import Firms
from handlers.base_handler import BaseHandler
from sqlconnector.models import State


class UserYearSummaryPortfolioHandler(BaseHandler):
    def get(self, **kwargs):
        self.check_and_update_states()
        self.write("\n".join(f"<p>{str(i.date)}: {i.get_dict()}</p>" for i in self.sql_conn.get_year_states()))

    def post(self, **kwargs):
        date = kwargs["date"]
        portfolio = {company_name: 100 for company_name in Firms.list_of_companies}
        self.sql_conn.post_states(
            [State(portfolio_state=portfolio, money=100000, date=datetime.date.fromisoformat(date))]
        )

    @staticmethod
    def get_handler_url():
        return "portfolio/*(?P<date>.*)"

    @staticmethod
    def get_api_version():
        return 1

    def check_and_update_states(self):
        def handle_transaction():

            # Если дата очередной транзакции не соответствует текущей рассматриваемой дате, сохраняем объект состояния
            # для текущей даты, и создаем для новой.
            if transaction.date != state_to_add.date:
                new_states.append(copy.deepcopy(state_to_add))
                state_to_add.date = transaction.date

            # Получаем имя компании в транзакции.
            company_in_transaction = transaction.company_name

            # Получаем дельту количества акций, с учётом знака соответствующего типу транзакции(-/+)
            number_of_stocks = transaction.number * pow(-1, not transaction.operation_type)

            # Если у текущего объекта состояния в описании портфеля нет компании, добавляем её с количеством акций = 0
            state_to_add.portfolio_state.setdefault(company_in_transaction, 0)

            # Изменяем текущее количество акций на дельту.
            state_to_add.portfolio_state[company_in_transaction] += number_of_stocks

            # Аналогично обновляем количество денежных средств.
            price = \
                prices[state_to_add.date]['prices'][company_in_transaction] * pow(-1, transaction.operation_type)
            state_to_add.money += price

        # Получаем последнюю запись о состоянии портфеля, для определения даты, с которой начинаем анализ.
        last_state = self.sql_conn.get_last_state()
        last_state_date = last_state.date
        current_date = datetime.datetime.now().date()
        new_states = []

        if last_state_date != current_date:
            # Определяем дельту по дням, для получения списка транзакций
            days_delta = (current_date - last_state_date).days - 1

            # Задаём дату ожидаемых первых новых транзакций, для которых не определено состояния портфеля
            current_state_date = datetime.datetime.now().date() - datetime.timedelta(days=days_delta)

            # Получаем список новых транзакций, для которых не определено состояния портфеля
            transactions = self.sql_conn.get_transactions(days_delta)

            # Получаем список цен за дни, для которых не определено состояния портфеля.
            prices = self.get_daily_prices(days_delta)

            # Создаем объект состояния портфеля, для наполнения и последующей отправки в базу
            state_to_add = State(date=current_state_date,
                                 portfolio_state=last_state.portfolio_state,
                                 money=last_state.money)

            for transaction in transactions:
                handle_transaction()

            self.sql_conn.post_states(new_states)

    def get_daily_prices(self, days=None):
        """
        The method creates a dictionary, where keys a dates and values a dictionaries {company_name: price}
        :return:  A dictionary, where keys a dates and values a dictionaries {company_name: price}
        """
        info = {}
        prices = self.sql_conn.get_daily_prices(days)
        for price in prices:
            info.setdefault(price.date, {}).setdefault("prices", {})[price.company_name] = price.price
        return info

