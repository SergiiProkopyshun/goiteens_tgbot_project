import datetime
def get_time_of_day():
    current_hour = datetime.datetime.now().hour
    if 6 <= current_hour < 12:
        return "Доброго ранку"
    elif 12 <= current_hour < 18:
        return "Доброго дня"
    elif 18 <= current_hour < 24:
        return "Доброго вечора"
    else:
        return "Доброї ночі"