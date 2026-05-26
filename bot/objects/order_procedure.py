from aiogram.fsm.state import StatesGroup, State


class OrderProcedure(StatesGroup):
    company_name = State()
    company_mail = State()
    order_name = State()
    order_price = State()
    order_description = State()