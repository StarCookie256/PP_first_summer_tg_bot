from aiogram import Router
from . import common, order, check_orders


def get_routers() -> list[Router]:

    return [
        check_orders.router,
        order.router,
        common.router,
    ]
