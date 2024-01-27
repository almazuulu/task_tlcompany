from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from decouple import config
import requests


API_TOKEN = config('TELEGRAM_API_TOKEN') 


# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Обычная клавиатура
button_weather = KeyboardButton('Узнать погоду')
keyboard_main = ReplyKeyboardMarkup(resize_keyboard=True).add(button_weather)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    Ответ на команды /start и /help.
    """
    await message.reply("Привет! Нажми на кнопку 'Узнать погоду', чтобы получить прогноз погоды.", reply_markup=keyboard_main)


@dp.message_handler(lambda message: message.text.lower() == 'узнать погоду')
async def ask_city(message: types.Message):
    """
    Спрашиваем у пользователя название города.
    """
    await message.reply("Пожалуйста, введите название города:")


@dp.message_handler()
async def get_weather(message: types.Message):
    """
    Получаем погоду для указанного города.
    """
    city = message.text
    try:
        # Отправляем запрос к нашему сервису на Django
        response = requests.get(f'http://0.0.0.0:8000/weather?city={city}')
        if response.status_code == 200:
            weather_data = response.json()
            formatted_response = f"Погода в {city}:\n\nТемпература: {weather_data['Температура']}\nДавление: {weather_data['Давление']}\nСкорость ветра: {weather_data['Скорость ветра']}"
            await message.reply(formatted_response)
        else:
            await message.reply(f"Не удалось получить погоду для города {city}.")
    except Exception as e:
        await message.reply(f"Ошибка: {e}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
