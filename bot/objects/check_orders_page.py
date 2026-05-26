from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.callback_data import CallbackData


class CheckOrdersPage(StatesGroup):
    end_left = State()
    end_right = State()
    middle = State()


class CheckPagination(CallbackData, prefix="chk_pag"):
    action: str
    page: str
    order_id: int


class CheckRemove(CallbackData, prefix="chk_rem"):
    order_id: int
