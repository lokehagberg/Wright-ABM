from copy import deepcopy
import numpy as np
from numpy.random import choice
import math
import matplotlib.pyplot as plt
import random 
#add venv

number_of_start_agents = 1000 #1000
start_total_wealth = 100000 #100000
start_agents = deepcopy(np.array([[start_total_wealth/number_of_start_agents, 0, 0]]*number_of_start_agents)) #deepcopy(np.array([[start_total_wealth/number_of_agents, 0]]*number_of_agents))

start_average_wage = 50 #50
start_wage_lb = start_average_wage - 40 #10
start_wage_ub = start_average_wage + 40 #90
start_market_value = 0 #0
start_bank_gains = 0 #0
start_time_steps = 15 #100 #12 for financial aspect
start_financial_aspect = True #False
loan_ub = 7*40
loan_lb = 7*40

#The three following sets are mutually disjoint

def is_employee(agents, agent):
    return(agents[agent][1] != 0)

def employers(agents):
    employers = [] 
    for i in range(len(agents)):
        if is_employee(agents=agents, agent=i):
            employers.append(agents[i][1])
    return(list(set(employers)))

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
    if math.floor(agents[consumer][0]) > 0:
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
            wage = choice(math.floor(wage_ub))
        agents[agent][0] += -wage
        agents[i][0] += wage

#The following make up financial aspects not included by Ian Wright
#The interest rates for loans are from P Termin 2004 Financial intermediation in the early Roman empire

def amortization(agents, agent):
    if (math.floor(agents[agent][2]) > 0) and (math.floor(agents[agent][0]) > 0):
        amortization = min(choice(math.floor(agents[agent][0])), agents[agent][2])
        agents[agent][0] += - amortization
        agents[agent][2] += - amortization

def loan(agents, agent): 
    if (0 >= math.floor(agents[agent][2])) and (math.floor(agents[agent][0]) > 0):
        loan = 0
        while (agents[agent][0]-loan_lb) >= loan: 
            loan = choice(math.floor(agents[agent][0] + loan_ub)) 
        agents[agent][0] += loan
        agents[agent][2] += loan 

def interest_effect(agents, bank_gains):
    loan_interest_rate = 3/1000 #between 3/1000 and 8/1000 historically except in rare cases (random.uniform(3, 8))/1000  
    saving_interest_rate = 1/1000 #between 0 and 3/1000   
    #Savings interest rates are always low enough to allow bank gains 
    for i in range(len(agents)):
        bank_gains += (agents[i][2] * loan_interest_rate) - (agents[i][0] * saving_interest_rate)
        agents[i][0] += agents[i][0] * saving_interest_rate
        agents[i][2] += agents[i][2] * loan_interest_rate 
    return(bank_gains)

#Credit inflation dominates M0 inflation
def credit_inflation_effect(agents, agent, bank_gains):
    if agent in employers(agents=agents):
        if math.floor(bank_gains) > 0:
            gain_taken = choice(math.floor(bank_gains))
            agents[agent][0] += gain_taken
            bank_gains += - gain_taken
    return(bank_gains)


def historical_development(agents, time_steps, financial_aspect):
    market_value = start_market_value
    total_wealth = start_total_wealth
    bank_gains = start_bank_gains
    average_wage=start_average_wage
    wage_lb = start_wage_lb
    wage_ub = start_wage_ub
    number_employed_month_list, number_unemployed_month_list, number_employers_month_list = [], [], []
    market_value_month_list, total_wage_bill_month_list, agents_month_list, debt_change_month_list, bank_gains_month_list, inflation_rate_month_list = [], [], [], [], [], []
    for i in range(time_steps):
        total_wage_bill = 0
        for j in range(len(agents)):
            value_before_wage, value_after_wage = [], []
            agent = selection(agents=agents)
            hiring(agents=agents, agent=agent, average_wage=average_wage)
            market_value = expenditure(agents=agents, agent=agent, market_value=market_value)
            market_value = market_sample(agents=agents, agent=agent, market_value=market_value)
            firing(agents=agents, agent=agent, average_wage=average_wage)
            for k in range(len(agents)):
                value_before_wage.append(agents[k][0])
            wage_payment(agents=agents, agent=agent, wage_lb=wage_lb, wage_ub=wage_ub)
            for k in range(len(agents)):
                value_after_wage.append(agents[k][0])
            total_wage_bill += np.dot(abs(np.asarray(value_after_wage) - np.asarray(value_before_wage)), np.array([1]*len(agents)))
            if financial_aspect:
                amortization(agents=agents, agent=agent)
                loan(agents=agents, agent=agent)
                bank_gains = credit_inflation_effect(agents=agents, agent=agent, bank_gains=bank_gains)
        #measure class composition, the firms by number of employed, market value, wage bill
        if financial_aspect:
            bank_gains = interest_effect(agents=agents, bank_gains=bank_gains)
        last_period_total_wealth = total_wealth
        total_wealth = deepcopy(total_wealth + bank_gains)
        if last_period_total_wealth != 0: 
            inflation_rate = total_wealth/last_period_total_wealth
        inflation_rate_month_list.append(inflation_rate)
        if financial_aspect:
            average_wage = (1 + inflation_rate) * average_wage
            wage_lb = average_wage - 40
            wage_ub = average_wage + 40

        agents_month_list.append(agents)
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
        total_debt = 0
        for i in range(len(agents)):
            total_debt += agents[i][2]
        debt_change_month_list.append(total_debt)
        bank_gains_month_list.append(bank_gains)

    return(number_employed_month_list, number_unemployed_month_list, number_employers_month_list,
    total_wage_bill_month_list, market_value_month_list, agents_month_list, debt_change_month_list, bank_gains_month_list, inflation_rate_month_list)


number_employed_month_list, number_unemployed_month_list, number_employers_month_list, total_wage_bill_month_list, market_value_month_list, agents_month_list, debt_change_month_list, bank_gains_month_list, inflation_rate_month_list = historical_development(agents=start_agents, time_steps=start_time_steps, financial_aspect=start_financial_aspect)


fig1 = plt.figure()
ax1 = fig1.add_subplot(1, 1, 1)
n, bins, patches = ax1.hist(number_employed_month_list)
ax1.set_xlabel('#Employed')
ax1.set_ylabel('Frequency')

fig2 = plt.figure()
ax2 = fig2.add_subplot(1, 1, 1)
n, bins, patches = ax2.hist(number_unemployed_month_list)
ax2.set_xlabel('#Unemployed')
ax2.set_ylabel('Frequency')

fig3 = plt.figure()
ax3 = fig3.add_subplot(1, 1, 1)
n, bins, patches = ax3.hist(number_employers_month_list)
ax3.set_xlabel('#Employers')
ax3.set_ylabel('Frequency')

fig4 = plt.figure()
ax4 = fig4.add_subplot(1, 1, 1)
n, bins, patches = ax4.hist(total_wage_bill_month_list)
ax4.set_xlabel('Total wage bill')
ax4.set_ylabel('Frequency')

fig5 = plt.figure()
ax5 = fig5.add_subplot(1, 1, 1)
n, bins, patches = ax5.hist(market_value_month_list)
ax5.set_xlabel('Market value')
ax5.set_ylabel('Frequency')

total_firm_revenue_month_list = []
for i in range(len(market_value_month_list) - 1):
    total_firm_revenue = market_value_month_list[i+1] - market_value_month_list[i]
    if 0 > total_firm_revenue:
        total_firm_revenue_month_list.append(-total_firm_revenue)
    else:
        total_firm_revenue_month_list.append(0)

fig6 = plt.figure()
ax6 = fig6.add_subplot(1, 1, 1)
n, bins, patches = ax6.hist(total_firm_revenue_month_list)
ax6.set_xlabel('Total firm revenue')
ax6.set_ylabel('Frequency')
#GDP is given by the total firm revenue over a year, the GDP growth can be derived from this
#Measure the number of months the above is below or above 1 to get the recession time
#The yearly wage share is the total wage bill per firm revenue a year
#100((revenue firm / wage ) - 1) is the rate of profit

total_wage_share_month_list = []
for i in range(len(total_firm_revenue_month_list)):
    if total_firm_revenue_month_list[i] != 0:
        total_wage_share_month_list.append(total_wage_bill_month_list[i]/total_firm_revenue_month_list[i])
    else:
        total_wage_share_month_list.append(1)

fig7 = plt.figure()
ax7 = fig7.add_subplot(1, 1, 1)
n, bins, patches = ax7.hist(total_wage_share_month_list)
ax7.set_xlabel('Total wage share')
ax7.set_ylabel('Frequency')

wealth_month_list, employers_month_list = [], []
for i in range(len(agents_month_list)):
    employers_month_list.append(employers(agents=agents_month_list[i]))
    per_agent_wealth_month_list = []
    for j in range(len(agents_month_list[0])):
        per_agent_wealth_month_list = agents_month_list[i][j][0]
    wealth_month_list.append(per_agent_wealth_month_list)
#Printing the agents wealth we get the wealth distribution monthly
#Checking the employers ceasing to be employers gives the firm demises
#Firm growth can easily be checked as well

non_unemployed_percentage_month_list = []
for i in range(len(number_unemployed_month_list)):
    non_unemployed_percentage_month_list.append(number_unemployed_month_list[i]/len(agents_month_list[0]))

fig8, axs = plt.subplots(2)
axs[0].plot(range(0,len(total_wage_share_month_list)), total_wage_share_month_list)
axs[1].plot(range(0,len(non_unemployed_percentage_month_list)), non_unemployed_percentage_month_list)

del non_unemployed_percentage_month_list[-1]
fig9 = plt.figure()
ax9 = fig9.add_subplot(1, 1, 1)
ax9.scatter(total_wage_share_month_list, non_unemployed_percentage_month_list)

#The three diagrams constructed above make up "Goodwin dynamics"

fig10, axs1 = plt.subplots(3)
axs1[0].plot(range(0,len(debt_change_month_list)), debt_change_month_list)
axs1[1].plot(range(0,len(bank_gains_month_list)), bank_gains_month_list)
axs1[2].plot(range(0,len(inflation_rate_month_list)), inflation_rate_month_list)

plt.show()

#Many agents having specialized behavior that is mechanical makes it less adaptive
#Network effects nor an intersectional analysis of agents attributes are observed here


 