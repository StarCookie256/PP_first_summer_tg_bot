from aiogram import Router, filters, F
from aiogram.types import Message

router = Router(name="common")


@router.message(filters.CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(f"Здравствуйте, {message.from_user.first_name}! Здесь можно подать заявку на создание "
                         f"продукта для своей компании от ИТ-Сферы!\n\nИспользуйте соответсвующую команду "
                         f"\"/order\" для этого")


@router.message(~F.text.startswith("/"))
async def any_message(message: Message) -> None:
    await message.answer("Используйте команду \"/order\" для запроса в компанию!")
