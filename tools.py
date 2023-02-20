from email.message import EmailMessage
from pywttr import Wttr

def compile():
    message = EmailMessage()
    subject, content = write()
    message.set_content(content)
    message['Subject'] = subject

    return message

def write():
    subject = 'Your Daily Kelvin Forecast'
    with open('message_body.txt', 'r', encoding='utf-8') as f:
        content = ''.join(f.readlines())

    content = content.format(*forecast())

    return subject, content

def forecast(city='Chicago'):
    wttr = Wttr(city)

    # Prevent HTTP timeout
    while True:
        try:
            forecast = wttr.en().weather[0]
            break
        except:
            print('Trying again...')
            continue
    # In normal units (celcius and kmh)
    high = int(forecast.maxtemp_c)
    low = int(forecast.mintemp_c)
    hourly_windspeed = []
    for hourly_item in forecast.hourly:
        hourly_windspeed.append(float(hourly_item.windspeed_kmph))
    windspeed = sum(hourly_windspeed)/len(hourly_windspeed)

    # Switch from Celcius to Kelvin
    high = int(high - 273.15)
    low = int(low - 273.15)
    # Switch from kmh to nanolightyears per second
    windspeed = int(windspeed * 10e9/2627980771.42)

    return high, low, windspeed