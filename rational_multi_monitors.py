from imperfect_information_monitor import ImperfectInformationMonitor
import spot
import metric
from vitamin_model_checker.model_checker_interface.explicit.RABATL import RABATL

class RationalMultiMonitors:
    def __init__(self, ltls_and_sims, ap, resource_bound, time_window):
        self.__ap = ap
        self.__monitors = [ImperfectInformationMonitor(ltl, ap, sim) for ltl,sim in ltls_and_sims] 
        self.__resource_bound = resource_bound
        self.__time_window = time_window
        self.__count = 0
        self.__backup_sim = [sim for _,sim in ltls_and_sims]
        self.__rabcgs = self.__generate_rabcgs()
        with open('tmp','w') as file:
            file.write(str(self.__rabcgs))
    def next(self, ev):
        if self.__count % self.__time_window == 0:
            self.__revise_and_evaluate()
        self.__count += 1
        ev.add('inv1')
        verdicts = []
        for i in range(len(self.__monitors)):
            verdicts.append(self.__monitors[i].next(ev)) # we do not need to project ev because sim in monitor has already been updated, so the monitor knows already how to handle the event properly
        return verdicts
    def __revise_and_evaluate(self, modifier=0):
        payoffs = []
        new_atoms = []
        for i in range(len(self.__monitors)):
            payoff = RationalMultiMonitors.get_payoffs(spot.formula(str(self.__monitors[i])), self.__backup_sim[i])
            for _ in range(modifier):
                for k in payoff:
                    if payoff[k] > 0:
                        payoff[k] = 0
                        break
            payoffs.append(payoff)
        sim_to_breaks = []
        for payoff in payoffs:
            sim_to_break = RationalMultiMonitors.knapsack(payoff, int(self.__resource_bound / len(self.__monitors)))
            atoms = []
            for sim in sim_to_break:
                # sim.remove('inv1')
                # sim.remove('inv2')
                atoms.append(sim[0])
                # sim.append('inv1')
                # sim.append('inv2')
            new_atoms.append(atoms)
            sim_to_breaks.append(sim_to_break)
        rabatl = self.__generate_rabatl(new_atoms)
        agreement_found = self.__solve_agreement_game(rabatl)
        if agreement_found:
            for i in range(len(self.__monitors)):
                new_sim = []
                for s in self.__monitors[i].get_sim():
                    if s not in sim_to_breaks[i]:
                        new_sim.append(s)
                self.__monitors[i].set_sim(new_sim)
        else:
            # print('No agreement could be found!')
            if modifier <= 2:
                # print('Try again!')
                self.__revise_and_evaluate(modifier+1)
            # else:
                # print('Give Up!')
        # print(f'broken sim: {sim_to_break}')
        # self.__sim = [s for s in self.__sim_backup if s not in sim_to_break]
    def __solve_agreement_game(self, rabatl):
        result = RABATL.model_checking(rabatl, 'tmp')
        return 'True' in result['initial_state']
    def __generate_rabatl(self, monitor_atoms):
        rabatl = '<' + ','.join([str(i) for i in range(1, len(self.__monitors)+1)]) + f'><{int(self.__resource_bound)}>F('
        rabatl_l = []
        for i in range(1, len(monitor_atoms)+1):
            if monitor_atoms[i-1]:
                rabatl_l.append(' && '.join([atom+f'{i}' for atom in monitor_atoms[i-1]]))
        if rabatl_l:
            rabatl += ' && '.join(rabatl_l)
        else:
            rabatl_l += 'false'
        rabatl += ')'
        return rabatl
    def __generate_rabcgs(self):
        number_of_agents = len(self.__monitors)
        monitors_visibility = []
        for monitor in self.__monitors:
            monitor_visibility = []
            for ap in self.__ap:
                if ap in ['inv1', 'inv2']: continue
                ok = True
                for sim in monitor.get_sim():
                    if ap in sim:
                        ok = False
                        break
                if ok:
                    monitor_visibility.append(ap)
            monitors_visibility.append(monitor_visibility)
        list_of_pairs = RationalMultiMonitors.generate_pairings(monitors_visibility)
        states = ' '.join([f's{i}' for i in range(len(list_of_pairs))])
        transitions = []
        costs = {}
        i = 0
        for state1 in list_of_pairs:
            transitions_state = []
            for state2 in list_of_pairs:
                monitors_actions = []
                if not [item for item in state1 if item not in state2]:
                    exchanges = [item for item in state2 if item not in state1]                
                    for monitor_visibility in monitors_visibility:
                        found = False
                        for exchange in exchanges:
                            if exchange[0] in monitor_visibility:
                                monitors_actions.append(f'{exchange[0]}')
                                found = True
                                # break
                            elif exchange[1] in monitor_visibility:
                                monitors_actions.append(f'{exchange[1]}')
                                found = True
                                # break
                        if not found:
                            monitors_actions.append('ii')
                        # else:
                        #     monitors_actions.append('ii')
                if len(monitors_actions) != len(monitors_visibility):
                    transitions_state.append('0')
                elif monitors_actions == ['ii']*4:
                    transitions_state.append('0')
                else:
                    for (atom1,atom2) in exchanges:
                        for j in range(1, len(monitors_visibility)+1):
                            if atom1 in monitors_visibility[j-1]:
                                break
                        for k in range(1, len(monitors_visibility)+1):
                            if atom2 in monitors_visibility[k-1]:
                                break
                        for ii in range(len(monitors_actions)):
                            if monitors_actions[ii] == atom1:
                                monitors_actions[ii] = monitors_actions[ii] + str(k)
                            if monitors_actions[ii] == atom2:
                                monitors_actions[ii] = monitors_actions[ii] + str(j)
                    transitions_state.append(''.join(monitors_actions))
                    if ''.join(monitors_actions) not in costs:
                        costs[''.join(monitors_actions)] = {}
                    costs[''.join(monitors_actions)][f's{i}'] = ','.join(['1']*len(self.__monitors))
            transitions.append(transitions_state)
            i += 1
        transitions_to_print = ''
        for transition in transitions:
            transitions_to_print += ' '.join(transition) + '\n'
        transitions_to_print = transitions_to_print[:-1]
        costs_to_print = ''
        for action in costs:
            costs_to_print += f'{action} '
            aux = []
            for state in costs[action]:
                aux.append(f'{state}${costs[action][state]}')
            costs_to_print += ';'.join(aux) + '\n'
        costs_to_print = costs_to_print[:-1]
        atomic_propositions = [f'{atom}{i}' for atom in self.__ap for i in range(1, len(self.__monitors)+1) if atom not in ['inv1', 'inv2']]
        atomic_propositions_to_print = ' '.join(atomic_propositions)
        labelling = ''
        for i in range(len(list_of_pairs)):
            state = list_of_pairs[i]
            for atom in atomic_propositions:
                if not state:
                    labelling += '0 '
                    continue
                for (atom1,atom2) in state:
                    for j in range(1, len(monitors_visibility)+1):
                        if atom1 in monitors_visibility[j-1]:
                            break
                    for k in range(1, len(monitors_visibility)+1):
                        if atom2 in monitors_visibility[k-1]:
                            break
                    if atom1+f'{k}' == atom or atom2+f'{j}' == atom:
                        ok = True
                        break
                    else:
                        ok = False
                if ok:
                    labelling += '1 '
                else:
                    labelling += '0 '
            labelling += '\n'
        labelling = labelling[:-1]
        return f'''Transition
{transitions_to_print}
Name_State
{states}
Initial_State
s0
Costs_for_actions_split
{costs_to_print}
Atomic_propositions
{atomic_propositions_to_print}
Labelling
{labelling}
Number_of_agents
{number_of_agents}'''
    @staticmethod
    def get_payoffs(phi, sim):
        payoffs = {}
        for s in sim:
            payoffs[str(s).replace('\'', '').replace(' ', '')] = 0.0
        atomic_propositions = spot.atomic_prop_collect(phi)
        for atomic_proposition in atomic_propositions:
            for s in payoffs:
                if atomic_proposition.to_str() in s.replace('[', '').replace(']', '').split(','):
                    payoffs[s] += metric.metric(phi, atomic_proposition.to_str())
        return payoffs
    @staticmethod
    def knapsack(payoffs, resource_bound):
        # Convert input dictionaries to lists for easier indexing
        atoms = list(payoffs.keys())
        payoff_values = [payoffs[atom] for atom in atoms]
        cost_values = [4 for atom in atoms]
        n = len(atoms)
        
        # Initialize the DP table
        dp = [[0.0 for _ in range(int(resource_bound * 100) + 1)] for _ in range(n + 1)]
        
        # Build the table in bottom-up manner
        for i in range(1, n + 1):
            for w in range(int(resource_bound * 100) + 1):
                if int(cost_values[i-1] * 100) <= w:
                    dp[i][w] = max(dp[i-1][w], dp[i-1][w - int(cost_values[i-1] * 100)] + payoff_values[i-1])
                else:
                    dp[i][w] = dp[i-1][w]
        
        # Find the items to include in the knapsack
        res = dp[n][int(resource_bound * 100)]
        w = int(resource_bound * 100)
        selected_atoms = []
        
        for i in range(n, 0, -1):
            if res <= 0:
                break
            if res == dp[i-1][w]:
                continue
            else:
                selected_atoms.append(atoms[i-1])
                res -= payoff_values[i-1]
                w -= int(cost_values[i-1] * 100)
        
        return [atom.replace('[', '').replace(']', '').replace('\'', '').split(',') for atom in selected_atoms]
    @staticmethod
    def generate_pairings(lists_of_lists):
        # Helper function to generate all unique pairs between two lists
        def get_pairs(lists):
            pairs = []
            for i, lst1 in enumerate(lists):
                for j, lst2 in enumerate(lists):
                    if i < j:  # Avoid duplicates (unordered pairs)
                        for a in lst1:
                            for b in lst2:
                                pair = (a, b) if a < b else (b, a)
                                pairs.append(pair)
            return pairs
        
        # Recursive backtracking function to generate all valid combinations of pairs
        def backtrack(current_pairs, remaining_items):
            # Add current combination to results
            result.append(current_pairs.copy())
            
            # Try to add more pairs if possible
            for pair in pairs:
                if pair[0] in remaining_items and pair[1] in remaining_items:
                    # Remove the paired elements from remaining items
                    remaining_items_copy = remaining_items.copy()
                    remaining_items_copy.remove(pair[0])
                    if pair[1] in remaining_items_copy:
                        remaining_items_copy.remove(pair[1])
                    
                    # Add the pair and recurse
                    current_pairs.append(pair)
                    backtrack(current_pairs, remaining_items_copy)
                    
                    # Backtrack by removing the last added pair
                    current_pairs.pop()

        # Step 1: Generate all pairs from the lists
        pairs = get_pairs(lists_of_lists)

        # Step 2: Backtrack to generate all valid combinations of pairs
        result = []
        all_items = set(item for sublist in lists_of_lists for item in sublist)
        
        backtrack([], all_items)
        
        return result