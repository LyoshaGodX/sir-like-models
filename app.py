import json
from flask import Flask, render_template, request
import numpy as np
from scipy import integrate

from sir_model import sir_model
from seir_model import seir_model
from seird_model import seird_model

app = Flask(__name__, static_folder='static')


# Определение маршрута для отображения страницы
@app.route('/')
def index():
    return render_template('index.html')


# Определение маршрута для обработки данных формы
@app.route('/update_plot', methods=['POST'])
def update_plot():
    # Получение данных из JSON-запроса
    data = request.get_json()

    # Извлечение значений из данных
    model = data['model']
    population = float(data['population'])
    simulation_time = int(data['time'])
    init_S = float(data['S'])
    init_E = float(data['E'])
    init_I = float(data['I'])
    init_R = float(data['R'])
    init_D = float(data['D'])
    R0 = float(data['R0'])
    gamma = float(data['gamma'])
    sigma = float(data['sigma'])
    mu = float(data['mu'])

    beta = R0 * gamma


    # Генерация данных для графика в зависимости от выбранной модели
    if model == 'SIR':
        # Генерация данных для модели SIR
        time_points = np.arange(simulation_time)
        initial_conditions = (init_S, init_I, init_R)
        solution = integrate.odeint(sir_model, initial_conditions, time_points, args=(population, beta, gamma))
        S = solution[:, 0]
        I = solution[:, 1]
        R = solution[:, 2]

        # Формирование данных графика
        plot_data = {'time': time_points.tolist(), 'S': S.tolist(), 'I': I.tolist(), 'R': R.tolist()}

    elif model == 'SEIR':
        # Генерация данных для модели SEIR
        time_points = np.arange(simulation_time)
        initial_conditions = (init_S, init_E, init_I, init_R)
        solution = integrate.odeint(seir_model, initial_conditions, time_points, args=(population, beta, gamma, sigma))
        S = solution[:, 0]
        E = solution[:, 1]
        I = solution[:, 2]
        R = solution[:, 3]

        # Формирование данных графика
        plot_data = {'time': time_points.tolist(), 'S': S.tolist(), 'E': E.tolist(), 'I': I.tolist(), 'R': R.tolist()}

    elif model == 'SEIRD':
        # Генерация данных для модели SEIRD
        time_points = np.arange(simulation_time)
        initial_conditions = (init_S, init_E, init_I, init_R, init_D)
        solution = integrate.odeint(seird_model, initial_conditions, time_points,
                                    args=(population, beta, gamma, sigma, mu))
        S = solution[:, 0]
        E = solution[:, 1]
        I = solution[:, 2]
        R = solution[:, 3]
        D = solution[:, 4]

        # Формирование данных графика
        plot_data = {'time': time_points.tolist(), 'S': S.tolist(), 'E': E.tolist(), 'I': I.tolist(), 'R': R.tolist(),
                     'D': D.tolist()}

    # Преобразование данных графика в формат JSON
    plot_json = json.dumps(plot_data)

    # Возврат данных графика в формате JSON
    return plot_json


if __name__ == '__main__':
    app.run(debug=True)