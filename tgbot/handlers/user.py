import datetime
import aiohttp
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.dispatcher.filters import Text

from tgbot.keyboards.inline import kbd, kbd2
from tgbot.misc.get_time import get_time_of_day
from tgbot.misc.states import SimpleStatsGroup


async def start_command(event: types.Message | types.CallbackQuery, state: FSMContext):
    if type(event) == types.CallbackQuery:
        await event.answer()
        message = event.message
    else:
        message = event
    time_of_day = get_time_of_day()
    await message.answer(
        f"<b>✋🏻 {time_of_day}! Я, радий надати Вам інформацію про погоду в будь-якому куточку світу. Для цього потрібно вписати місто, яке вас цікавить, і я надам вам дані про прогноз погоди.</b>\n\n<i>Зверніть увагу: деякі міста потрібно писати лише англійською мовою.</i>",
        reply_markup=kbd2)
    await state.finish()

async def get_weather(message: types.Message, state: FSMContext):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Хмарно \U00002601",
        "Rain": "Дощ \U00002614",
        "Drizzle": "Дощ \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Сніг \U0001F328",
        "Mist": "Туман \U0001F32B"
    }
    config = message.bot['config']
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={config.weather.token}&units=metric') as response:
                data = await response.json()

        city = data["name"]
        region = data["sys"]["country"]
        cur_weather = data["main"]["temp"]

        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Подивіться у вікно, не розумію, що там за погода!"

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'http://api.openweathermap.org/data/2.5/forecast?q={message.text}&appid={config.weather.token}&units=metric') as response:
                forecast_data = await response.json()

        forecast_message = "\n<i>Прогноз погоди на 6 днів:</i>\n"
        current_date = None
        for forecast in forecast_data["list"]:
            forecast_date = datetime.datetime.fromtimestamp(forecast["dt"]).date()
            if current_date is None or current_date != forecast_date:
                forecast_message += f"\n<b>{forecast_date.strftime('%Y-%m-%d %A')}</b>\n\n"
                current_date = forecast_date

            forecast_time = datetime.datetime.fromtimestamp(forecast["dt"]).time()
            forecast_temp = forecast["main"]["temp"]
            forecast_weather_description = forecast["weather"][0]["main"]
            if forecast_weather_description in code_to_smile:
                forecast_wd = code_to_smile[forecast_weather_description]
            else:
                forecast_wd = "Подивіться у вікно, не розумію, що там за погода!"

            forecast_message += f"<i>{forecast_time.strftime('%H:%M')}</i> | {forecast_temp}°C | {forecast_wd}\n\n"

        await message.reply(
            f"<b>📃 Погода у вибраному регіоні:</b>\n____________________________\n\n"
            f"<i>Дата та час: </i>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"<i>Погода у місті: </i>{city}, {region}\n<i>Температура: </i>{cur_weather}°C | {wd}\n____________________________\n\n"
            f"<i>Вологість: </i>{humidity}%\n<i>Тиск: </i>{pressure} мм.рт.ст.\n<i>Вітер: </i>{wind} м/с\n____________________________\n\n"
            f"<i>Схід сонця: </i>{sunrise_timestamp.strftime('%H:%M')}\n<i>Захід сонця: </i>{sunset_timestamp.strftime('%H:%M')}\n<i>Тривалість дня: </i>{length_of_the_day}\n____________________________\n"
            f"{forecast_message}", reply_markup=kbd)
        await state.finish()
    except:
        await message.reply("<b>🟡 Не вдалося отримати дані про погоду. Перевірте правильність написання назви міста.</b>\n\n<i>Зверніть увагу: деякі міста потрібно писати лише англійською мовою.</i>")

async def city(call: types.CallbackQuery):
    await call.message.answer("<b>🌤 Введіть місто, в якому хочете дізнатись погоду.</b>")
    await SimpleStatsGroup.state1.set()

async def press_button(message: types.Message):
    await message.answer("<b>ℹ️ Щоб дізнатися погоду Вам потрібно натиснути на кнопку під повідомленням, і після чого ввести потрібне Вам місто.</b>", reply_markup=kbd2)



def register_user(dp: Dispatcher):
    dp.register_callback_query_handler(city, text="weather_check", state="*")
    dp.register_callback_query_handler(start_command, text="menu", state="*")
    dp.register_message_handler(start_command, commands=["start"], state="*")
    dp.register_message_handler(get_weather, state=SimpleStatsGroup.state1)
    dp.register_message_handler(press_button)