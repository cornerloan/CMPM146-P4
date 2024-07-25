import pyhop
import json
import inspect

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
        new_name = f"op_{name.replace(' ', '_')}"
        tasks.append((new_name, ID))

        return tasks

    return method

def declare_methods(data):
    # some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first
    
	# your code here
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)
    # Organize recipes by the product they produce
    product_recipes = {}
    for name, rule in data['Recipes'].items():
        for product in rule['Produces']:
            if product not in product_recipes:
                product_recipes[product] = []
            product_recipes[product].append((name, rule))

    # Iterate through each product and sort its recipes by time
    for product, recipes in product_recipes.items():
        # Sort the recipes by time (ascending)
        sorted_recipes = sorted(recipes, key=lambda x: x[1].get('Time', float('inf')))
        
        # Create methods for each sorted recipe
        methods = [make_method(name, rule) for name, rule in sorted_recipes]
        pyhop.declare_methods(f'produce_{product}', *methods)

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
            current_amount = getattr(state, item)
            current_amount[ID] -= amount
            setattr(state, item, current_amount)

        # Update state by producing output
        for item, amount in rule.get('Produces', {}).items():
            current_amount = getattr(state, item)
            current_amount[ID] += amount
            setattr(state, item, current_amount)

        # Update the remaining time and return the new state
        state.time[ID] -= rule.get('Time', 0)
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
        if depth > 100:
            return True
        return False
    
    #prevent recrafting of any tools
    def avoid_recrafting_tools(state, curr_task, tasks, plan, depth, calling_stack):
        if curr_task[0].startswith('produce_'):
            item = curr_task[0].split('_', 1)[1]
            if item in data['Tools'] and getattr(state, item)[ID] > 0:
                return True
        return False
    
    #prevent producing and item which would amount to the player having more than 40 of an item
    def avoid_recrafting_items(state, curr_task, tasks, plan, depth, calling_stack):
        if curr_task[0].startswith('produce_'):
            item = curr_task[0].split('_', 1)[1]
            if item in data['Items'] and getattr(state, item)[ID] > 35:
                return True
        return False
    

    pyhop.add_check(heuristic)
    pyhop.add_check(avoid_recrafting_tools)
    pyhop.add_check(avoid_recrafting_items)

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

    state = set_up_state(data, 'agent', time=100)
    goals = set_up_goals(data, 'agent')
    
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')

    # pyhop.print_operators()
    # pyhop.print_methods()

    # Hint: verbose output can take a long time even if the solution is correct; 
    # try verbose=1 if it is taking too long
    pyhop.pyhop(state, goals, verbose=1)
    # pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)

    # pyhop.print_state(state)
