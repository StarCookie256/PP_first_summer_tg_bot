import os
import json

DATA_FILE = "orders.json"


async def load_from_json() -> list:
    try:
        if await _file_exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        else:
            return []
    except Exception as e:
        print(f"Ошибка при загрузке файла --> {e}")


async def save_to_json(new_data):
    try:
        orders_data = await load_from_json()

        order_id = len(orders_data)+1
        orders_data.append({"id": order_id, **new_data})

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(orders_data, f, ensure_ascii=False, indent=4, sort_keys=True)
    except Exception as e:
        print(f"Ошибка при загрузке файла --> {e}")


async def remake_json(new_data: list):
    try:
        for i, data in enumerate(new_data):
            data['id'] = i+1

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=4, sort_keys=True)
    except Exception as e:
        print(f"Ошибка при загрузке файла --> {e}")


async def _file_exists() -> bool:
    return os.path.isfile(DATA_FILE)
