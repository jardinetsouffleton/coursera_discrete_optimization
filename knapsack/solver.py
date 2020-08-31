#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import pandas as pd
Item = namedtuple("Item", ['index', 'value', 'weight'])

class Solver:
    def __init__(self, input_data):
        full_data = pd.read_csv(input_data, header=None, sep=' ', names=['value', 'weight'])
        self.item_count = full_data.iloc[0,0]
        self.capacity= full_data.iloc[0,1]
        self.data = full_data.iloc[1:]
#         self.data['taken'] = 0
        self.total_weight = 0
    
    def get_objective(self):
        selected = self.data[self.data['taken']==1]
        
        if self.solution_mode == 'dp':
            return str(selected['value'].sum()) + ' 1'
        else:
            return str(selected['value'].sum()) + ' 0'
    
    def get_selected(self):
        if 'index' in self.data.columns:
            self.data = self.data.sort_values('index')
        out = ''
        for i in range(len(self.data)):
            out += str(self.data.iloc[i]['taken'])[0]+ ' '
        
        return out
    
    def greedy_relative_value(self):
        self.data['relative_value'] = self.data['value']/self.data['weight']
        self.data = self.data.sort_values('relative_value', ascending=False)
        self.data['index'] = self.data.index
        taken = []
        for i in range(len(self.data)):

            if self.total_weight + self.data.iloc[i]['weight'] <= self.capacity:
                idx = self.data.iloc[i]['index']
#                 self.data.loc[idx, 'taken'] = 1
                taken.append(1)
                self.total_weight += self.data.iloc[i]['weight']

            else:
                taken.append(0)
                continue
        print(self.total_weight - self.capacity)
        self.data['taken'] = taken
        
        self.solution_mode = 'greedy'
        
        return self.get_objective() + '\n' +self.get_selected()
    
    def dp_recurrent(self, k, j):
        """
        Returns optimal value for knapsack with capacity k and number of items j
        """
        if k==0:
            return 0
        elif self.data.iloc[j]['weight'] <= k:
            return max(self.dp_recurrent(k, j-1), self.data.iloc[j] + self.dp_recurrent(k-self.data.iloc[j]['weight'], j-1))
        else:
            return self.dp_recurrent(k, j-1)
    
    def compute_dp_table(self):
        """
        Computes the table associated with the problem to solve it with dynamic programming
        """
        self.dp_table = [[0 for i in range(self.item_count + 1)] for j in range(self.capacity + 1)]
        
        # computing the table
        for items in range(self.item_count + 1):
            for weight in range(self.capacity + 1):
                if items == 0 or weight == 0:
                    self.dp_table[weight][items] = 0
                elif self.data.iloc[items-1]['weight'] <= weight:
                    self.dp_table[weight][items] = max(self.dp_table[weight][items-1], self.data.iloc[items-1]['value'] + self.dp_table[weight-self.data.iloc[items-1]['weight']][items-1])
                else:
                    self.dp_table[weight][items] = self.dp_table[weight][items-1]
    
    def dp_solution(self):
        """
        returns solution for dynamic programming solution
        """
        self.compute_dp_table()
        # start at optimal solution and trace back to beginning
        capacity = self.capacity
        items = self.item_count
        value = self.dp_table[capacity][items]
        taken = [] #list that will hold binary values indicating whether or not this item was selected
        
        while value != 0:
#             print(f'taken: {taken}')
#             print(f'value: {value}')
            
            if self.dp_table[capacity][items-1] == value:
                items -=1
                taken.insert(0, 0)
#                 continue
            else:
                taken.insert(0,1)
                capacity -= self.data.iloc[items-1]['weight']
                items -=1
                value = self.dp_table[capacity][items]
#                 continue
            
        if not len(taken) == len(self.data):
            extension = [0] * (len(self.data) - len(taken))
            taken = extension + taken
        self.data['taken'] = taken
        
        self.solution_mode = 'dp'
        
        return  self.get_objective() + '\n' +self.get_selected()
    
    def branch_and_bound(self, method='linear'):
        """
        linear: linear relaxation
        """



def solve_it(input_data):
    # Modify this code to run your optimization algorithm
    solver = Solver(input_data)
    
    # prepare the solution in the specified output format
    # output_data = str(value) + ' ' + str(0) + '\n'
    # output_data += ' '.join(map(str, taken))
    output = solver.dp_solution()
    del solver
    return output


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(file_location))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')
