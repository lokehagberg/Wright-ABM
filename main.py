from copy import deepcopy
import numpy as np
from numpy.random import choice
import matplotlib.pyplot as plt


agents = []              
total_wealth = 100000
start_wage_lb = 0
start_wage_ub = 10
start_average_wage = 5
start_market_value = 0


#The three following sets are mutually disjoint

def is_employee(agent):
    return(agents[agent][1] != 0)

def employers():
    employers = [] 
    for i in range(len(agents)):
        if is_employee(i):
            employers.append(agents[i][1])
    return(employers)

def is_unemployed(agent):
    return((not is_employee(agent)) and (agent not in employers))

#The following are the rules

def selection():
    return(choice(len(agents)) - 1)

def hiring(agent, average_wage):
    if not is_employee(agent):
        potential_employer_wealth = []
        total_potential_employer_wealth = 0
        for i in range(len(agents)):
            if is_employee(i) == 0:
                potential_employer_wealth.append(agents[i][0])
                total_potential_employer_wealth += agents[i][0]
            else: 
                potential_employer_wealth.append(0.0)
        picked_employer = choice(agents, p=(potential_employer_wealth/total_potential_employer_wealth)) - 1
        if agents[picked_employer][0] > average_wage:
            agents[agent][1] = picked_employer

def expenditure(agent, market_value):
    consumer = agent
    while consumer == agent:
        consumer = choice(agents) 
    expense = choice(agents[consumer][0])
    agents[consumer][1] += -expense
    market_value += expense
    return(market_value)

def market_sample(agent, market_value):
    if not is_unemployed(agent):
        sample = choice(market_value)
        market_value += -sample
        if agents[agent][1] == 0:
            agents[agent][0] += sample
        else: 
            agents[agents[agent][1]][0] += sample
        return(market_value)

def firing(agent, average_wage): 
    if agent in agents.employers:
        number_of_employed = 0
        employed = []
        for i in range(agents):
            if agents[i][1] == agent:
                number_of_employed += 1
                employed.append[i]
        number_fired = max((number_of_employed-(agents[agent][0]/average_wage)),0)    
        for i in range(number_fired):
            fired = choice(employed)
            employed.remove(fired)
            agents[fired][1] = 0


def wage_payment(agent, wage_lb, wage_ub):
    if agent in agents.employers:
        for i in range(agents):
            if agents[i][1] == agent:
                wage = 0
                while wage < wage_lb:
                    wage = choice(wage_ub)
                agents[agent][0] += -wage
                agents[i][0] += wage

def historical_development(time_steps):
    market_value = start_market_value
    for i in range(time_steps):
        for j in range(len(agents)):
            agent = selection(agents)
            hiring(agent, start_average_wage)
            market_value = expenditure(agent, market_value)
            market_value = market_sample(agent, market_value)
            firing(agent, start_average_wage)
            wage_payment(agent, start_wage_lb, start_wage_ub)
        

#100 time steps is the ordinary

#measure classes
#measure number of employed in what number of firms (by employer)
#firm growth per month
#firm demises per month
#GDP: the total firm revenue / previous
#measure the number of months the above is below or above 1 
#the wage share is the total wage bill per firm revenue a year
#wealth distribution per year
#100((revenue firm / wage ) - 1) is the rate of profit
                


        


    



 