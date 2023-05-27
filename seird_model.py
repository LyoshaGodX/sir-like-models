import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate
from scipy.optimize import minimize
from parse_json import parse_in_date


def seird_model(y, t, N, beta, gamma, sigma, mu):
    S, E, I, R, D = y
    dSdt = -beta * S * I / N
    dEdt = beta * S * I / N - sigma * E
    dIdt = sigma * E - gamma * I - mu * I
    dRdt = gamma * I
    dDdt = mu * I
    return dSdt, dEdt, dIdt, dRdt, dDdt


def optimize_seird_parameters(population, total_confirmed_stat, total_recovered_stat, total_deaths_stat):
    # Time points for integration (adjust as per your data)
    time_points = np.arange(len(total_confirmed_stat))

    # Define the objective function
    def objective(params):
        R0, gamma, sigma, mu = params
        beta = R0 * gamma
        initial_conditions = (population - total_confirmed_stat[0], total_confirmed_stat[0], 0,
                              total_recovered_stat[0], total_deaths_stat[0])
        solution = integrate.odeint(seird_model, initial_conditions, time_points,
                                    args=(population, beta, gamma, sigma, mu))
        infected = solution[:, 2]
        recovered = solution[:, 3]
        deaths = solution[:, 4]
        correct_confirmed_stat = np.array(total_confirmed_stat) - np.array(total_recovered_stat) - np.array(
            total_deaths_stat)
        error = np.sum((infected - correct_confirmed_stat) ** 2) + \
                np.sum((recovered - total_recovered_stat) ** 2) + \
                np.sum((deaths - total_deaths_stat) ** 2)
        return error

    # Set the initial parameter values and bounds
    initial_params = np.array([2, 1 / 7, 1 / 6, 1.94 / 100])  # Initial guess for the parameters
    bounds = [(1.4, 5.7), (1/18, 1/4), (1 / 14, 1 / 2), (0.5/100, 3 / 100)]
    # Run the optimization
    result = minimize(objective, initial_params, bounds=bounds, options={"maxiter": 1000000})

    # Extract the optimized parameter values
    optimized_params = result.x

    return optimized_params


def plot_seird_model(N, beta, gamma, sigma, mu, initial_conditions, duration):
    # Time points for integration
    time_points = np.linspace(0, duration, num=1000)

    # Integrate the SEIRD model
    solution = integrate.odeint(seird_model, initial_conditions, time_points,
                                args=(N, beta, gamma, sigma, mu))
    S = solution[:, 0]
    E = solution[:, 1]
    I = solution[:, 2]
    R = solution[:, 3]
    D = solution[:, 4]

    # Plotting the SEIRD model
    plt.figure(figsize=(10, 6))
    plt.plot(time_points, S, 'b-', label='Susceptible')
    plt.plot(time_points, E, 'y-', label='Exposed')
    plt.plot(time_points, I, 'r-', label='Infected')
    plt.plot(time_points, R, 'g-', label='Recovered')
    plt.plot(time_points, D, 'm-', label='Deaths')
    plt.xlabel('Time')
    plt.ylabel('Number of Individuals')
    plt.title('SEIRD Model')
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_real_vs_model_data(time_points, total_confirmed_stat, total_recovered_stat, total_deaths_stat,
                            population, beta, gamma, sigma, mu, initial_conditions):
    # Integrate the SEIRD model using the optimized parameters
    solution = integrate.odeint(seird_model, initial_conditions, time_points,
                                args=(population, beta, gamma, sigma, mu))
    infected_model = solution[:, 2]
    recovered_model = solution[:, 3]
    deaths_model = solution[:, 4]
    correct_confirmed_stat = np.array(total_confirmed_stat) - np.array(total_recovered_stat) - np.array(
        total_deaths_stat)

    # Plotting the results
    plt.figure(figsize=(10, 6))
    plt.plot(time_points, correct_confirmed_stat, 'ro', label='Real Infected')
    plt.plot(time_points, total_recovered_stat, 'go', label='Real Recovered')
    plt.plot(time_points, total_deaths_stat, 'bo', label='Real Deaths')
    plt.plot(time_points, infected_model, 'b-', label='Model Infected')
    plt.plot(time_points, recovered_model, 'm-', label='Model Recovered')
    plt.plot(time_points, deaths_model, 'c-', label='Model Deaths')
    plt.xlabel('Days')
    plt.ylabel('Number of Individuals')
    plt.title('SEIRD Model - Real Data vs. Model Data')
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    # Load data
    population = 5398064
    total_confirmed_stat, total_recovered_stat, total_deaths_stat = parse_in_date('covid_data.json', "24.03.2020",
                                                                                  "24.12.2020")

    # Set the initial conditions for the SEIRD model using the first values from the data
    initial_conditions = (population - total_confirmed_stat[0], total_confirmed_stat[0], 0,
                          total_recovered_stat[0], total_deaths_stat[0])

    # Optimize the parameters
    optimized_params = optimize_seird_parameters(population, total_confirmed_stat, total_recovered_stat,
                                                 total_deaths_stat)

    # Calculate the coefficient of infectivity (R0)
    R0, gamma_optimized, sigma_optimized, mu_optimized = optimized_params
    beta_optimized = R0 * gamma_optimized

    print("Optimized Parameters:")
    print("Beta:", beta_optimized)
    print("Gamma:", gamma_optimized)
    print("Sigma:", sigma_optimized)
    print("Mu:", mu_optimized)
    print("Coefficient of Infectivity (R0):", R0)

    # Time points for integration (adjust as per your data)
    time_points = np.arange(len(total_confirmed_stat))

    plot_seird_model(population, beta_optimized, gamma_optimized, sigma_optimized, mu_optimized,
                     initial_conditions, 2000)

    plot_real_vs_model_data(time_points, total_confirmed_stat, total_recovered_stat, total_deaths_stat,
                            population, beta_optimized, gamma_optimized, sigma_optimized, mu_optimized,
                            initial_conditions)


if __name__ == '__main__':
    main()
