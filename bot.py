import json
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_AUTH_TOKEN = os.getenv('API_AUTH_TOKEN')

API_URL = "http://127.0.0.1:5000/api/check-imei"

WHITE_LIST_USERS = {6248416489}

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()


def clean_text(text: str) -> str:
    if not text:
        return "Неизвестно"

    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")  # Экранирование HTML
    return text


@dp.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id
    if user_id not in WHITE_LIST_USERS:
        await message.answer("У вас нет доступа к этому боту.")
        return
    await message.answer("Отправьте IMEI, чтобы проверить информацию.")


@dp.message()
async def check_imei(message: Message):
    user_id = message.from_user.id
    if user_id not in WHITE_LIST_USERS:
        await message.answer("У вас нет доступа к этому боту.")
        return

    imei = message.text.strip()
    if not (imei.isdigit() and len(imei) == 15):
        await message.answer("Некорректный IMEI. Должно быть ровно 15 цифр.")
        return

    headers = {"Content-Type": "application/json"}
    payload = {"imei": imei, "token": API_AUTH_TOKEN}

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        await message.answer(f"Ошибка запроса к API: {clean_text(str(e))}")
        return
    except json.JSONDecodeError:
        await message.answer("Ошибка обработки JSON-ответа от API.")
        return

    # print(json.dumps(data, indent=4, ensure_ascii=False))

    if "details" in data:
        try:
            details = json.loads(data["details"])
            if "properties" in details:
                device_info = details["properties"]
            else:
                await message.answer("Ошибка: В `details` нет `properties`.")
                return
        except json.JSONDecodeError:
            await message.answer("Ошибка обработки `details` в JSON.")
            return
    else:
        await message.answer("Ошибка: В ответе API нет `details`.")
        return

    device_name = clean_text(device_info.get("deviceName", "Неизвестно"))
    image_url = device_info.get("image", "")
    imei = clean_text(device_info.get("imei", "Неизвестно"))
    imei2 = clean_text(device_info.get("imei2", "Неизвестно"))
    serial = clean_text(device_info.get("serial", "Неизвестно"))
    sim_lock = "🔒 Заблокирован" if device_info.get("simLock") else "🔓 Разблокирован"
    model_desc = clean_text(device_info.get("modelDesc", "Неизвестно"))
    replacement = "♻️ Был заменён" if device_info.get("replacement") else "✅ Оригинальное"
    demo_unit = "🛠 Это демонстрационный образец" if device_info.get("demoUnit") else "🚀 Обычный серийный образец"
    apple_region = clean_text(device_info.get("apple/region", "Неизвестно"))
    apple_model = clean_text(device_info.get("apple/modelName", "Неизвестно"))
    lost_mode = "⚠️ Устройство в режиме пропажи!" if device_info.get("lostMode") else "✅ Не числится потерянным"

    message_text = f"""🔍 <b>Информация об устройстве:</b>
📱 <b>Модель:</b> {device_name}
📷 <b>Изображение:</b> <a href="{image_url}">Ссылка</a>
📟 <b>IMEI 1:</b> {imei}
📟 <b>IMEI 2:</b> {imei2}
📦 <b>Серийный номер:</b> {serial}
🔄 <b>SIM-Lock:</b> {sim_lock}
📌 <b>Описание модели:</b> {model_desc}
🔁 <b>Замена устройства:</b> {replacement}
🎛 <b>Тип устройства:</b> {demo_unit}
🌍 <b>Регион Apple:</b> {apple_region}
🍏 <b>Модель Apple:</b> {apple_model}
🔎 <b>Статус пропажи:</b> {lost_mode}
"""

    await message.answer(message_text, parse_mode="HTML", disable_web_page_preview=False)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
