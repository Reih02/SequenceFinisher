import re
import random
import copy

INTEGER = r'^[0-9]+$'

def is_valid_expression(object, function_symbols, leaf_symbols):
    if type(object) is int or object in leaf_symbols or re.match(INTEGER, str(object)): # leaf node
        return True
    
    if type(object) is list and len(object) == 3 and object[0] in function_symbols: # list
        if is_valid_expression(object[1], function_symbols, leaf_symbols) and is_valid_expression(object[2], function_symbols, leaf_symbols):
           return True

    return False 


def depth(expression, depth_count = 0):
    if not type(expression) is list:
        return depth_count

    else:
        return max(depth(expression[1], depth_count=depth_count+1), depth(expression[2], depth_count=depth_count+1))


def evaluate(expression, bindings):
    if not type(expression) is list:
        if type(expression) is int:
            return expression
        if isinstance(expression, tuple):
            expression = expression[1]
            try:
                return bindings[expression[0]](evaluate(expression[1], bindings), evaluate(expression[2], bindings))
            except:
                return 0
        if expression in bindings:
            return bindings[expression]
    try:
        return bindings[expression[0]](evaluate(expression[1], bindings), evaluate(expression[2], bindings))
    except:
        return 0

def check_distinctness(expressions):
    counter = 0
    seen_expressions = []
    i = 0
    while i < len(expressions):
        if expressions[i] not in seen_expressions:
            seen_expressions.append(expressions[i])
            counter += 1
        i += 1
    print(f"Distinct expressions: {counter}")
    return counter >= 1000

def check_diversity(expressions, max_depth):
    counts = [0 for i in range(0, max_depth + 1)]
    for expression in expressions:
        print(expression)
        expression_depth = depth(expression)
        counts[expression_depth] += 1

    print(f"Counts: {counts}")
    print(f"Sum of counts: {sum(counts)}")

    for count in counts:
        if count < 100:
            return False
    return True

def check_validness(expressions, function_symbols, leaves):
    for expression in expressions:
        if not is_valid_expression(expression, function_symbols, leaves):
            return False
    return True


# function_symbols = ['+', '-', '/', '*']
# leaves = list(range(-9, 9))
# max_depth = 3

# expressions = [random_expression(function_symbols, leaves, max_depth)
#                for _ in range(10000)]

# if check_diversity(expressions, max_depth):
#     print("Diversity OK!")
# else:
#     print("Diversity failed :(")

# if check_distinctness(expressions):
#     print("Distinctness OK!")
# else:
#     print("Distinctness failed :()")

# if check_validness(expressions, function_symbols, leaves):
#     print("Validness OK!")
# else:
#     print("Validness failed :()")


def generate_rest(initial_sequence, expression, length):
    new_items = []
    working_sequence = copy.deepcopy(initial_sequence)
    while length > 0:
        bindings = {'x': working_sequence[-2], 'y': working_sequence[-1], 'i': len(working_sequence),
                    '+': lambda x, y: x + y, '-': lambda x, y: x - y, '*': lambda x, y: x * y}
        new_item = evaluate(expression, bindings)
        new_items.append(new_item)
        working_sequence.append(new_item)
        length -= 1
    return new_items

def random_expression(function_symbols, leaves, max_depth):
        if random.random() > 0.5 or max_depth == 0: # return a leaf node
            return random.choice(leaves)
        else: # return a random expression tree
            return [random.choice(function_symbols), random_expression(function_symbols, leaves, max_depth-1), random_expression(function_symbols, leaves, max_depth-1)]
        
def predict_rest(sequence):
    leaves = ['x', 'y', 'i'] + list(range(-2, 3))
    population = []
    gen_number = 30000
    for i in range(gen_number):
        current_random = random_expression(['+', '-', '*'], leaves, 3)
        current_fitness = fitness(current_random, sequence, 0)
        population.append((current_fitness, current_random))

        
    while len(population) > 100 or len(population) == 0:
        
        for individual in population:
            if not isinstance(individual, tuple):
                population.remove(individual)
            else:
                individual = (fitness(individual[1], sequence, 0), individual[1])

        next_generation_select = select(population, gen_number)
        

        next_generation_mutate = [mutate(random.choice(population), leaves) for x in range(0, int(len(population) * 0.1))]
        for i in range(0, len(next_generation_mutate)):
            if not isinstance(next_generation_mutate[i], tuple):
                next_generation_mutate[i] = (fitness(next_generation_mutate[i], sequence, 0), next_generation_mutate[i])


        next_generation_crossover = []
        for i in range(10):
            random_expression_1 = random.choice(population)
            random_expression_2 = random.choice(population)
            if random_expression_1 != random_expression_2:
                random_expression_1, random_expression_2 = crossover(random_expression_1, random_expression_2)
            next_generation_crossover.append(random_expression_1)
            next_generation_crossover.append(random_expression_2)

        gen_number = int(gen_number / 10)

        population = next_generation_select + next_generation_mutate + next_generation_crossover

        population_sorted = sorted(population, key=lambda x: x[0])
        best_individual = population_sorted[-1]
        i = 1
        while len(set(generate_rest(sequence, population_sorted[-i], 5))) > 1:
            best_individual = population_sorted[-i]
            i += 1

    return generate_rest(sequence, best_individual, 5)

    


def mutate(expression, leaves):
    flattened_tree = []
    stack = [expression[1]]

    while stack:
        node = stack.pop()
        if isinstance(node, list):
            flattened_tree.append(node)
            stack.extend(node[1:])
        else:
            flattened_tree.append(node)
    try:
        random_node = random.choice(flattened_tree[1:])
    except IndexError:
        return (expression[0], expression)
    if isinstance(random_node, list):
        random_node[:] = [random_expression(['+', '-', '*'], leaves, random.randint(0, 3))]
    else:
        return random_expression(['+', '-', '*'], leaves, random.randint(0, 3))

    return (expression[0], expression)

def crossover(expression1, expression2):
    flattened_tree1 = []
    flattened_tree2 = []
    stack1 = [expression1[1]]
    stack2 = [expression2[1]]

    while stack1:
        node = stack1.pop()
        if isinstance(node, list):
            flattened_tree1.append(node)
            stack1.extend(node[1:])
        else:
            flattened_tree1.append(node)

    while stack2:
        node = stack2.pop()
        if isinstance(node, list):
            flattened_tree2.append(node)
            stack2.extend(node[1:])
        else:
            flattened_tree2.append(node)

    try:
        random_node_1 = random.choice(flattened_tree1[1:])
        random_node_2 = random.choice(flattened_tree2[1:])
    except IndexError:
        return (expression1, expression2)

    if isinstance(random_node_1, list) and isinstance(random_node_2, list):
        random_node_1[:], random_node_2[:] = random_node_2[:], random_node_1[:]
    else:
        return ((expression1[0], random_node_1), (expression2[0], random_node_2))

    return ((expression1[0], expression1), (expression2[0], expression2))
    

def select(population, gen_number):
    winning_individuals = []
    for i in range(int(gen_number / 10)):
        competitors = []
        for i in range(100):
            competitors.append(random.choice(population))
        winner = sorted(competitors, key=lambda x: x[0])[-1]
        winning_individuals.append(winner)
    return winning_individuals
        

    


def fitness(expression, sequence, current_iter):
    # See how well the expression worked on the last elements of the input
    score = 0
    answer = sequence[(-3 - current_iter):]
    test = generate_rest(sequence[0:(len(sequence) - (3 + current_iter))], expression, (3 + current_iter))
    for i in range(0, len(test)):
        if test[i] == answer[i]:
            score += 1
    
    return score
