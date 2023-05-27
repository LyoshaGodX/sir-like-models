import requests
import json
from datetime import datetime
import pandas as pd
import warnings


def get_covid_data(url, file_name):
    response = requests.get(url)
    data = response.json()

    to_del = ["h1", "last_update", "description", "source_name", "url", "title"]

    for key in to_del:
        del data[key]

    array_of_data = [data['delta'], data['total']]

    for case in array_of_data:
        for key, value in case.items():
            if isinstance(value, list):
                target_year = 2020
                for item in value:
                    if item['date'] == '01.01':
                        target_year += 1
                    current_date = datetime.strptime(item['date'], '%d.%m')
                    current_date = current_date.replace(year=target_year)
                    formatted_date = current_date.strftime('%d.%m.%Y')
                    item['date'] = formatted_date

    formatted_json = json.dumps(data, indent=4, ensure_ascii=False)

    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(formatted_json)


def parse_in_date(json_file, start_date, end_date):
    warnings.simplefilter(action='ignore', category=UserWarning)

    # Загрузка JSON файла
    with open(json_file) as file:
        data = json.load(file)

    # Создание DataFrame для всех данных из JSON
    total_recovered = pd.DataFrame(data['total']['recovered'])
    total_confirmed = pd.DataFrame(data['total']['confirmed'])
    total_deaths = pd.DataFrame(data['total']['deaths'])

    # Преобразование столбца 'date' в тип datetime
    total_recovered['date'] = pd.to_datetime(total_recovered['date'], format='%d.%m.%Y')
    total_confirmed['date'] = pd.to_datetime(total_confirmed['date'], format='%d.%m.%Y')
    total_deaths['date'] = pd.to_datetime(total_deaths['date'], format='%d.%m.%Y')

    # Фильтрация по интервалу дат
    filtered_recovered = total_recovered[
        (total_recovered['date'] >= start_date) & (total_recovered['date'] <= end_date)]
    filtered_confirmed = total_confirmed[
        (total_confirmed['date'] >= start_date) & (total_confirmed['date'] <= end_date)]
    filtered_deaths = total_deaths[
        (total_deaths['date'] >= start_date) & (total_deaths['date'] <= end_date)]

    # Получение значений confirmed, recovered и deaths
    confirmed_values = filtered_confirmed['value'].tolist()
    recovered_values = filtered_recovered['value'].tolist()
    deaths_values = filtered_deaths['value'].tolist()

    return confirmed_values, recovered_values, deaths_values


def main():
    data_url = 'https://news.mail.ru/ajax/coronavirus/stat/tab/region/91/'
    file_name = 'covid_data.json'
    start_date, end_date = "24.03.2020", "26.03.2020"
    get_covid_data(data_url, file_name)
    print(parse_in_date(file_name, start_date, end_date))


if __name__ == '__main__':
    main()
