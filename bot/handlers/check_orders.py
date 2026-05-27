from aiogram import F, Router, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from bot.objects import CheckOrdersPage, CheckPagination, CheckRemove
from application_layer.json_saver import load_from_json, remake_json
import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
router = Router(name="check_orders")


@router.message(filters.Command("check_orders"))
async def cmd_check_orders(message: types.Message, state: FSMContext) -> None:
    if message.from_user.id != ADMIN_ID:
        await message.answer(f"Команда доступна только с правами администратора!")
        return

    initial_message = await message.answer("Загрузка новых заказов...")
    await state.set_state(CheckOrdersPage.middle)

    fake_callback = types.CallbackQuery(
        id="0",  # Любой ID строки
        from_user=message.from_user,  # Пользователь из команды
        chat_instance="0",  # Любой ID чата
        message=initial_message,  # (!) Передаем только что созданное сообщение бота
        data=CheckPagination(action="prev", page="end_left", order_id=2).pack() # Имитируем callback_data
    )

    # 3. Напрямую вызываем callback-хэндлер и передаем ему наш фейк
    await cmd_check_end_left(callback=fake_callback, state=state,
                             callback_data=CheckPagination(action="prev",page="end_left", order_id=2))


async def get_inline_buttons(order_id: int, back_action: str = None, next_action: str = None):
    buttons = [types.InlineKeyboardButton(text="❌ Удалить",
                                          callback_data=CheckRemove(order_id=order_id).pack())]

    if back_action:
        buttons.append(types.InlineKeyboardButton(text="⬅️ Назад",
                                                  callback_data=CheckPagination(action="prev",
                                                                                page=back_action,
                                                                                order_id=order_id).pack()))
    if next_action:
        buttons.append(types.InlineKeyboardButton(text="Далее ➡️",
                                                  callback_data=CheckPagination(action="next",
                                                                                page=next_action,
                                                                                order_id=order_id).pack()))
    return types.InlineKeyboardMarkup(inline_keyboard=[buttons])


async def _load_order(order_id: int) -> dict:
    data = await load_from_json()
    order = next((x for x in data if x['id'] == order_id), None)
    if not order:
        return {}

    order_text = f"<i>Заявка на разработку №{order['id']}/{len(data)}:</i>\n" \
           f"👜 <b>Компания-заказчик</b>:" \
                 f"\n\t\t <code>{order['company_name']}</code>\n" \
           f"📧 Почта компании:" \
                 f"\n\t\t <code>{order['company_mail']}</code>\n" \
           f"💵 <b>Оплата разработки в размере:</b>" \
                 f"\n\t\t <code>{order['order_price']} руб.</code>\n" \
           f"✏ <b>Краткое название проекта:</b>" \
                 f"\n\t\t <code>{order['order_name']}</code>\n" \
           f"📝 Подробное описание:" \
                 f"\n\t\t <code>{order['order_description']}</code>"

    final_data = {"order_text": order_text, "orders_count": len(data)}

    return final_data


@router.callback_query(CheckOrdersPage.middle, CheckPagination.filter(F.page == "end_left"))
@router.callback_query(CheckOrdersPage.end_right, CheckPagination.filter(F.page == "end_left"))
async def cmd_check_end_left(callback: types.CallbackQuery, state: FSMContext, callback_data: CheckPagination) -> None:
    await state.set_state(CheckOrdersPage.end_left)
    callback_data.order_id -= 1
    curr_order = await _load_order(callback_data.order_id)
    action = None

    if len(list(curr_order.keys())) <= 0:
        await callback.message.edit_text(
            text="Заказов сейчас нет"
        )
        return

    if curr_order['orders_count'] > callback_data.order_id+1:
        action = "middle"
    elif curr_order['orders_count'] == callback_data.order_id+1:
        action = "end_right"

    buttons = await get_inline_buttons(next_action=action, order_id=callback_data.order_id)
    await callback.message.edit_text(
        text=curr_order['order_text'],
        parse_mode=ParseMode.HTML,
        reply_markup=None if buttons == [] else buttons
    )


@router.callback_query(CheckOrdersPage.end_left, CheckPagination.filter(F.page == "middle"))
@router.callback_query(CheckOrdersPage.end_right, CheckPagination.filter(F.page == "middle"))
@router.callback_query(CheckOrdersPage.middle, CheckPagination.filter(F.page == "middle"))
async def cmd_check_middle(callback: types.CallbackQuery, state: FSMContext, callback_data: CheckPagination) -> None:
    await state.set_state(CheckOrdersPage.middle)

    if callback_data.action == "prev":
        callback_data.order_id -= 1
    elif callback_data.action == "next":
        callback_data.order_id += 1

    curr_order = await _load_order(callback_data.order_id)
    back_action = None
    next_action = None

    # вперед
    if curr_order['orders_count'] > callback_data.order_id+1:
        next_action = "middle"
    elif curr_order['orders_count'] == callback_data.order_id+1:
        next_action = "end_right"
    # назад
    if callback_data.order_id-1 > 1:
        back_action = "middle"
    elif callback_data.order_id-1 == 1:
        back_action = "end_left"

    buttons = await get_inline_buttons(back_action=back_action, next_action=next_action, order_id=callback_data.order_id)
    await callback.message.edit_text(
        text=curr_order['order_text'],
        parse_mode=ParseMode.HTML,
        reply_markup=None if buttons == [] else buttons
    )


@router.callback_query(CheckOrdersPage.middle, CheckPagination.filter(F.page == "end_right"))
@router.callback_query(CheckOrdersPage.end_left, CheckPagination.filter(F.page == "end_right"))
async def cmd_check_end_right(callback: types.CallbackQuery, state: FSMContext, callback_data: CheckPagination) -> None:
    await state.set_state(CheckOrdersPage.end_right)
    callback_data.order_id += 1
    curr_order = await _load_order(callback_data.order_id)
    action = None

    if callback_data.order_id - 1 > 1:
        action = "middle"
    elif callback_data.order_id - 1 == 1:
        action = "end_left"

    buttons = await get_inline_buttons(back_action=action, order_id=callback_data.order_id)
    await callback.message.edit_text(
        text=curr_order['order_text'],
        parse_mode=ParseMode.HTML,
        reply_markup=None if buttons == [] else buttons
    )


@router.callback_query(CheckRemove.filter())
async def cmd_delete_order(callback: types.CallbackQuery, callback_data: CheckRemove) -> None:
    data_full = await load_from_json()

    for data in data_full:
        if data['id'] == callback_data.order_id:
            data_full.remove(data)
            break

    await remake_json(data_full)

    await callback.message.edit_text(
        text="Запись успешно удалена"
    )
