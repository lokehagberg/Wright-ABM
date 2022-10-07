from copy import deepcopy
import numpy as np
from numpy.random import choice
import matplotlib.pyplot as plt

class ABM:
    
    def __init__(self,
                 agents:                list = [],
                 total_wealth:          int = 100000,
                 start_wage_lb:         int = 0,
                 start_wage_ub:         int = 10,
                 start_average_wage:    int = 5,
                 start_market_value:    int = 0
                 ):
        self.agents = agents
        self.total_wealth = total_wealth
        self.start_wage_lb = start_wage_lb
        self.start_wage_ub = start_wage_ub
        self.start_average_wage = start_average_wage
        self.start_market_value = start_market_value
    
    def is_employee(self, agent):
        return(self.agents[agent][1] != 0)

    def employers(self):
        employers = [] 
        for i in range(len(self.agents)):
            if self.agents[i][1] != 0:
                employers.append(self.agents[i][1])
        return(employers)

    def is_unemployed(self, agent):
        return((self.agents[agent][1] == 0) and (agent not in self.employers))
    
    def selection(self):
        return(choice(len(self.agents)) - 1)
    
    def hiring(self, agent, average_wage):
        if not self.is_employee(agent):
            proto_probability_of_hire = []
            potential_employer_wealth = 0
            for i in range(len(self.agents)):
                if self.is_employee(i) == 0:
                    proto_probability_of_hire.append(self.agents[i][0])
                    potential_employer_wealth += self.agents[i][0]
                else: 
                    proto_probability_of_hire.append(0.0)
            picked_employer = choice(self.agents, p=(proto_probability_of_hire/potential_employer_wealth)) - 1
            if self.agents[picked_employer][0] > average_wage:
                self.agents[agent][1] = picked_employer

    def expenditure(self, agent, market_value):
        consumer = agent
        while consumer == agent:
            consumer = choice(self.agents) 
        expense = choice(self.agents[consumer][0])
        self.agents[consumer][1] += -expense
        market_value += expense
        return(market_value)
    
    def market_sample(self, agent, market_value):
        if self.agents.unemployed == 0:
            sample = choice(market_value)
            market_value += -sample
            if self.agents[agent][1] == 0:
                self.agents[agent][0] += sample
            else: 
                self.agents[self.agents[agent][1]][0] += sample
            return(market_value)

    def firing(self, agent, average_wage): 
        if agent in self.agents.employers:
            number_of_employed = 0
            employed = []
            for i in range(self.agents):
                if self.agents[i][1] == agent:
                    number_of_employed += 1
                    employed.append[i]
            number_fired = max((number_of_employed-(self.agents[agent][0]/average_wage)),0)    
            for i in range(number_fired):
                fired = choice(employed)
                employed.remove(fired)
                self.agents[fired][1] = 0

    
    def wage_payment(self, agent, wage_lb, wage_ub):
        if agent in self.agents.employers:
            for i in range(self.agents):
                if self.agents[i][1] == agent:
                    wage = 0
                    while wage < wage_lb:
                        wage = choice(wage_ub)
                    self.agents[agent][0] += -wage
                    self.agents[i][0] += wage
    
    def historical_development(self, time_steps):
        market_value = self.start_market_value
        for i in range(time_steps):
            for j in range(len(self.agents)):
                agent = self.agents.selection
                self.agents.hiring(agent, self.start_average_wage)
                market_value = self.agents.expenditure(agent, market_value)
                market_value = self.agents.market_sample(agent, market_value)
                self.agents.firing(agent, self.start_average_wage)
                self.agents.wage_payment(agent, self.start_wage_lb, self.start_wage_ub)
            

test_1_ABM = ABM
test_1_ABM.time_steps(100)

#measure classes
#measure number of employed in what number of firms (by employer)
#firm growth per month
#firm demises per month
#GDP: the total firm revenue / previous
#measure the number of months the above is below or above 1 
#the wage share is the total wage bill per firm revenue a year
#wealth distribution per year
#100((revenue firm / wage ) - 1) is the rate of profit
                


        


    



 