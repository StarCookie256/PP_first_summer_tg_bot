from aiogram import F, Router, types, filters
from aiogram.fsm.context import FSMContext
from bot.objects import OrderProcedure
from application_layer.json_saver import save_to_json

router = Router(name="order")


@router.message(filters.Command("order"))
async def procedure_order(message: types.Message, state: FSMContext) -> None:
    await state.set_state(OrderProcedure.company_name)
    await message.answer("Напишите имя компании, которая хочет подать заявку (не более 50 символов)")


@router.message(OrderProcedure.company_name, F.text)
async def procedure_company_name(message: types.Message, state: FSMContext):
    if message.text is None:
        await message.answer("Пожалуйста, отправьте текстовое сообщение с названием.")
        return

    company_name = message.text.strip()
    if len(company_name) > 50:
        await message.answer("❌ Название компании не может превышать 50 символов. Попробуйте ещё раз:")
        return
    await state.update_data(company_name=company_name)
    await state.set_state(OrderProcedure.company_mail)
    await message.answer("Хорошо, записал. Теперь отправьте сюда почту компании")


@router.message(OrderProcedure.company_mail, F.text)
async def procedure_company_mail(message: types.Message, state: FSMContext):
    if message.text is None:
        await message.answer("Пожалуйста, отправьте текстовое сообщение с почтой.")
        return

    # Для почты валидация не требуется, но можно при желании добавить простую проверку
    await state.update_data(company_mail=message.text.strip())
    await state.set_state(OrderProcedure.order_name)
    await message.answer("Хорошо, записал. Теперь напишите краткое описание или название заявки/проекта (не более 50 символов)")


@router.message(OrderProcedure.order_name, F.text)
async def procedure_order_name(message: types.Message, state: FSMContext):
    if message.text is None:
        await message.answer("Пожалуйста, отправьте текстовое сообщение с наименованием заказа.")
        return

    order_name = message.text.strip()
    if len(order_name) > 50:
        await message.answer("❌ Краткое название не может превышать 50 символов. Попробуйте ещё раз:")
        return
    await state.update_data(order_name=order_name)
    await state.set_state(OrderProcedure.order_price)
    await message.answer("Хорошо, записал. Теперь напишите сумму (только цифры), которая пойдёт на разработку продукта")


@router.message(OrderProcedure.order_price, F.text)
async def procedure_order_price(message: types.Message, state: FSMContext):
    if message.text is None:
        await message.answer("Пожалуйста, отправьте текстовое сообщение с ценой заказа.")
        return

    price_raw = message.text.strip()
    # Проверяем, что введены только цифры (целое положительное число)
    if not price_raw.isdigit():
        await message.answer("❌ Пожалуйста, введите только цифры (целое положительное число). Попробуйте ещё раз:")
        return
    price = int(price_raw)  # можно сохранить как int или str
    await state.update_data(order_price=price)
    await state.set_state(OrderProcedure.order_description)
    await message.answer("Хорошо, записал. Теперь напишите подробное описание проекта (не более 777 символов)")


@router.message(OrderProcedure.order_description, F.text)
async def procedure_order_desc(message: types.Message, state: FSMContext):
    if message.text is None:
        await message.answer("Пожалуйста, отправьте текстовое сообщение с описанием заказа.")
        return

    description = message.text.strip()
    if len(description) > 777:
        await message.answer("❌ Длинное описание не может превышать 777 символов. Попробуйте ещё раз:")
        return
    await state.update_data(order_description=description)

    order_data = await state.get_data()
    await save_to_json(order_data)

    await message.answer("Заявка успешно обработана и отправлена ✅")
    await state.clear()
