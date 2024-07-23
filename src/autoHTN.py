import pyhop
import json

def check_enough(state, ID, item, num):
    if getattr(state, item)[ID] >= num:
        return []
    return False

def produce_enough(state, ID, item, num):
    return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods('have_enough', check_enough, produce_enough)

def produce(state, ID, item):
    return [('produce_{}'.format(item), ID)]

pyhop.declare_methods('produce', produce)

def make_method(name, rule):
    def method(state, ID):
        # your code here
        tasks = []

        # Add tasks to check if required items are available
        for item, amount in rule.get('Requires', {}).items():
            tasks.append(('have_enough', ID, item, amount))

        # Add tasks to check if consumed items are available
        for item, amount in rule.get('Consumes', {}).items():
            tasks.append(('have_enough', ID, item, amount))

        # Add production task
        tasks.append(('produce', ID, name))

        return tasks

    return method

def declare_methods(data):
    # some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first
    
	# your code here
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)
    methods = []

    # Iterate through all the recipes
    for name, rule in data['Recipes'].items():
        # Create the method with a safe name
        method = make_method(name, rule)
        method_name = 'produce_' + rule['Produces'].keys().__iter__().__next__()
        pyhop.declare_methods(method_name, method)

def make_operator(rule):
    def operator(state, ID):
        # your code here
        # Check if there is enough time for this action
        if state.time[ID] < rule.get('Time', 0):
            return False

        # Check if we have the correct tool
        for item, amount in rule.get('Requires', {}).items():
            if getattr(state, item)[ID] < amount:
                return False

        # Check if all consumable items are available
        for item, amount in rule.get('Consumes', {}).items():            
            if getattr(state, item)[ID] < amount:
                return False

        # Update state by consuming resources
        for item, amount in rule.get('Consumes', {}).items():
            getattr(state, item)[ID] -= amount

        # Update state by producing output
        for item, amount in rule.get('Produces', {}).items():
            getattr(state, item)[ID] += amount

        # Update the remaining time
        state.time[ID] -= rule.get('Time', 0)

        # Operator always returns the modified state
        return state

    return operator

def declare_operators(data):
    # your code here
	# hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)
    operators = []

    # Iterate through each recipe
    for recipe_name, rule in data['Recipes'].items():
        # Get the current operator
        operator = make_operator(rule)

        # Make the naming scheme correct and add it to the list of operators
        operator.__name__ = f"op_{recipe_name.replace(' ', '_')}"
        operators.append(operator)

    # Declare this list as valid operators
    pyhop.declare_operators(*operators)


def add_heuristic(data, ID):
    # prune search branch if heuristic() returns True
	# do not change parameters to heuristic(), but can add more heuristic functions with the same parameters:
	# e.g. def heuristic2(...); pyhop.add_check(heuristic2)

    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        # your code here
        
		# end branch if depth is too far
        if depth > 10:
            return True
        return False

    pyhop.add_check(heuristic)

def set_up_state(data, ID, time=0):
    state = pyhop.State('state')
    state.time = {ID: time}

    for item in data['Items']:
        setattr(state, item, {ID: 0})

    for item in data['Tools']:
        setattr(state, item, {ID: 0})

    for item, num in data['Initial'].items():
        setattr(state, item, {ID: num})

    return state

def set_up_goals(data, ID):
    goals = []
    for item, num in data['Goal'].items():
        goals.append(('have_enough', ID, item, num))

    return goals

if __name__ == '__main__':
    rules_filename = 'crafting.json'

    with open(rules_filename) as f:
        data = json.load(f)

    state = set_up_state(data, 'agent', time=239) # allot time here
    goals = set_up_goals(data, 'agent')
    
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')

    pyhop.print_operators()
    pyhop.print_methods()

    # Hint: verbose output can take a long time even if the solution is correct; 
    # try verbose=1 if it is taking too long
    pyhop.pyhop(state, goals, verbose=3)
    # pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)

    pyhop.print_state(state)