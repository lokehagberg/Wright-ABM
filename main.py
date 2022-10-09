from copy import deepcopy
import numpy as np
from numpy.random import choice
import math
import matplotlib.pyplot as plt

number_of_agents = 1000 #1000
start_total_wealth = 100000 #100000
start_agents = deepcopy(np.array([[start_total_wealth/number_of_agents, 0]]*number_of_agents)) #deepcopy(np.array([[start_total_wealth/number_of_agents, 0]]*number_of_agents))
start_wage_lb = 10 #10
start_wage_ub = 90 #90
start_average_wage = 50 #50
start_market_value = 0 #0
start_time_steps = 100 #100

#The three following sets are mutually disjoint

def is_employee(agents, agent):
    return(agents[agent][1] != 0)

def employers(agents):
    employers = [] 
    for i in range(len(agents)):
        if is_employee(agents=agents, agent=i):
            employers.append(agents[i][1])
    return(employers)

def is_unemployed(agents, agent):
    return((not is_employee(agents=agents, agent=agent)) and (agent not in employers(agents=agents)))

#The following are the rules

def selection(agents):
    return(choice(len(agents)))

def hiring(agents, agent, average_wage):
    if not is_employee(agents=agents, agent=agent):
        potential_employer_wealth = []
        total_potential_employer_wealth = 0
        for i in range(len(agents)):
            if is_employee(agents=agents, agent=i) == 0:
                potential_employer_wealth.append(max(agents[i][0],0.0))
                total_potential_employer_wealth += max(agents[i][0], 0.0)
                #If the wealth is negative the probability is zero
            else: 
                potential_employer_wealth.append(0.0)
        picked_employer_probability = []
        for i in range(len(potential_employer_wealth)):
            picked_employer_probability.append(potential_employer_wealth[i]/total_potential_employer_wealth)
        picked_employer = choice(len(agents), p=(picked_employer_probability)) 
        if agents[picked_employer][0] > average_wage:
            agents[agent][1] = picked_employer

def expenditure(agents, agent, market_value):
    consumer = agent
    while consumer == agent:
        consumer = choice(len(agents)) 
    if agents[consumer][0] > 0:
        expense = choice(math.floor(agents[consumer][0]))
    else:
        expense = 0.0
    agents[consumer][0] += -expense
    market_value += expense
    return(market_value)

def market_sample(agents, agent, market_value):
    if not is_unemployed(agents=agents, agent=agent):
        sample = 0
        if market_value > 0:
            sample = choice(math.floor(market_value))
        market_value += -sample
        if agents[agent][1] == 0:
            agents[agent][0] += sample
        else: 
            agents[math.floor(agents[agent][1])][0] = deepcopy(agents[math.floor(agents[agent][1])][0] + sample) 
        return(market_value)
    else:
        return(market_value)

def firing(agents, agent, average_wage): 
    if agent in employers(agents=agents):
        number_of_employed = 0
        employed = []
        for i in range(len(agents)):
            if agents[i][1] == agent:
                number_of_employed += 1
                employed.append(i)
        number_fired = max((number_of_employed-(agents[agent][0]/average_wage)),0)  
        for i in range(math.floor(number_fired)):
            if employed != []:
                fired = choice(employed)
                employed.remove(fired)
                agents[fired][1] = 0

def wage_payment(agents, agent, wage_lb, wage_ub):
    if agent not in employers(agents=agents):
        return

    for i in range(len(agents)):
        if agents[i][1] != agent:
            continue

        wage = 0
        while wage < wage_lb:
            wage = choice(wage_ub)
        agents[agent][0] += -wage
        agents[i][0] += wage

def historical_development(agents, time_steps):
    market_value = start_market_value
    number_employed_month_list, number_unemployed_month_list, number_employers_month_list = [], [], []
    market_value_month_list, total_wage_bill_month_list = [], []
    for i in range(time_steps):
        total_wage_bill = 0
        for j in range(len(agents)):
            value_before_wage, value_after_wage = [], []
            agent = selection(agents=agents)
            hiring(agents=agents, agent=agent, average_wage=start_average_wage)
            market_value = expenditure(agents=agents, agent=agent, market_value=market_value)
            market_value = market_sample(agents=agents, agent=agent, market_value=market_value)
            firing(agents=agents, agent=agent, average_wage=start_average_wage)
            for k in range(len(agents)):
                value_before_wage.append(agents[k][0])
            wage_payment(agents=agents, agent=agent, wage_lb=start_wage_lb, wage_ub=start_wage_ub)
            for k in range(len(agents)):
                value_after_wage.append(agents[k][0])
            total_wage_bill += np.dot(abs(np.asarray(value_after_wage) - np.asarray(value_before_wage)), np.array([1]*len(agents)))
        #measure class composition, the firms by number of employed, market value, wage bill
        number_employed, number_unemployed = 0, 0
        firm_size_month_list = []
        for j in range(len(agents)): 
            firm_size_month_list.append(employers(agents=agents).count(j))
            if is_employee(agents=agents, agent=j):
                number_employed += 1
            elif is_unemployed(agents=agents, agent=j):
                number_unemployed += 1
        number_employed_month_list.append(number_employed)
        number_unemployed_month_list.append(number_unemployed)
        number_employers_month_list.append(len(agents) - number_employed - number_unemployed)
        total_wage_bill_month_list.append(total_wage_bill)
        market_value_month_list.append(market_value)
    return(number_employed_month_list, number_unemployed_month_list, number_employers_month_list,
    total_wage_bill_month_list, market_value_month_list)

#The total removed market value one month divided by the previous is the GDP growth
#Measure the number of months the above is below or above 1 to get the recession time
#The wage share is the total wage bill per firm revenue a year
#Printing the agents wealth we get the wealth distribution monthly
#Checking the employers ceasing to be employers gives the firm demises
#Firm growth can easily be checked as well
#100((revenue firm / wage ) - 1) is the rate of profit

number_employed_month_list, number_unemployed_month_list, number_employers_month_list, total_wage_bill_month_list, market_value_month_list = historical_development(agents=start_agents, time_steps=start_time_steps)

print(number_employed_month_list)
fig, axs = plt.subplots(1, 1,
                        figsize =(10, 7),
                        tight_layout = True)
axs.hist(number_employed_month_list)
plt.show()



 