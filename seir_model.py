import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate
from scipy.optimize import minimize
from parse_json import parse_in_date
import timeit


def seir_model(y, t, N, beta, gamma, sigma):
    S, E, I, R = y
    dSdt = -beta * S * I / N
    dEdt = beta * S * I / N - sigma * E
    dIdt = sigma * E - gamma * I
    dRdt = gamma * I
    return dSdt, dEdt, dIdt, dRdt


def optimize_seir_parameters(population, total_confirmed_stat, total_recovered_stat):
    # Time points for integration (adjust as per your data)
    time_points = np.arange(len(total_confirmed_stat))

    # Define the objective function
    def objective(params):
        R0, gamma, sigma = params
        beta = R0 * gamma
        initial_conditions = (population - total_confirmed_stat[0], total_confirmed_stat[0], 0, total_recovered_stat[0])
        solution = integrate.odeint(seir_model, initial_conditions, time_points, args=(population, beta, gamma, sigma))
        infected = solution[:, 2]
        recovered = solution[:, 3]
        correct_confirmed_stat = np.array(total_confirmed_stat) - np.array(total_recovered_stat)
        error = np.sum((infected - correct_confirmed_stat) ** 2) + np.sum((recovered - total_recovered_stat) ** 2)
        return error

    # Set the initial parameter values and bounds
    initial_params = np.array([1.4, 1/18, 1/14])  # Initial guess for the parameters
    bounds = [(1.4, 5.7), (1/18, 1/4), (1/14, 1/2)]  # Bounds for the parameters
    # Run the optimization
    result = minimize(objective, initial_params, bounds=bounds, options={'maxiter': 10000000})

    # Extract the optimized parameter values
    optimized_params = result.x

    return optimized_params


def plot_seir_model(N, beta, gamma, sigma, initial_conditions, duration):
    # Time points for integration
    time_points = np.linspace(0, duration, num=1000)

    # Integrate the SEIR model
    solution = integrate.odeint(seir_model, initial_conditions, time_points, args=(N, beta, gamma, sigma))
    S = solution[:, 0]
    E = solution[:, 1]
    I = solution[:, 2]
    R = solution[:, 3]

    # Plotting the SEIR model
    plt.figure(figsize=(10, 6))
    plt.plot(time_points, S, 'b-', label='Susceptible')
    plt.plot(time_points, E, 'y-', label='Exposed')
    plt.plot(time_points, I, 'r-', label='Infected')
    plt.plot(time_points, R, 'g-', label='Recovered')
    plt.xlabel('Time')
    plt.ylabel('Number of Individuals')
    plt.title('SEIR Model')
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_real_vs_model_data(time_points, total_confirmed_stat, total_recovered_stat, population,
                            beta, gamma, sigma, initial_conditions):
    # Integrate the SEIR model using the optimized parameters
    solution = integrate.odeint(seir_model, initial_conditions, time_points,
                                args=(population, beta, gamma, sigma))
    infected_model = solution[:, 2]
    recovered_model = solution[:, 3]

    correct_confirmed_stat = np.array(total_confirmed_stat) - np.array(total_recovered_stat)

    # Plotting the results
    plt.figure(figsize=(10, 6))
    plt.plot(time_points, correct_confirmed_stat, 'ro', label='Real Infected')
    plt.plot(time_points, total_recovered_stat, 'go', label='Real Recovered')
    plt.plot(time_points, infected_model, 'b-', label='Model Infected')
    plt.plot(time_points, recovered_model, 'm-', label='Model Recovered')
    plt.xlabel('Days')
    plt.ylabel('Number of Individuals')
    plt.title('SEIR Model - Real Data vs. Model Data')
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    # Load data
    population = 5398064
    total_confirmed_stat, total_recovered_stat, _ = parse_in_date('covid_data.json', "24.03.2020", "24.05.2020")

    # Set the initial conditions for the SEIR model using the first values from the data
    initial_conditions = (population - total_confirmed_stat[0], total_confirmed_stat[0], 0, total_recovered_stat[0])

    # Optimize the parameters
    optimized_params = optimize_seir_parameters(population, total_confirmed_stat, total_recovered_stat)

    # Calculate the coefficient of infectivity (R0)
    R0, gamma_optimized, sigma_optimized = optimized_params
    beta_optimized = R0*gamma_optimized
    print("Optimized Parameters:")
    print("Beta:", beta_optimized)
    print("Gamma:", gamma_optimized)
    print("Sigma:", sigma_optimized)
    print("Coefficient of Infectivity (R0):", R0)

    # Time points for integration (adjust as per your data)
    time_points = np.arange(len(total_confirmed_stat))

    plot_seir_model(population, beta_optimized, gamma_optimized, sigma_optimized, initial_conditions, 720)

    plot_real_vs_model_data(time_points, total_confirmed_stat, total_recovered_stat, population,
                            beta_optimized, gamma_optimized, sigma_optimized, initial_conditions)


if __name__ == '__main__':
    execution_time = timeit.timeit(main, number=1)
    print("Время выполнения: ", execution_time, "секунд")
