# TODO import your packages
import numpy as np
import operator
from common import scorer
from sklearn.preprocessing import OrdinalEncoder as oe

def ord_pizzas(pizzas):
    oe = OrdinalEncoder()
    ae.fit(pizzas)
    enc_pizzas = oe.transform(pizzas)
    pizza_idxs = np.array([i for i in range(len(pizzas))])
    return ord_pizzas, old_id, new_id

class Pizza():
    def __init__(self, pizza, idx):
        self.score = len(set(pizza))
        self.idx = idx
    def __repr__(cls):
        return 'pizza :)'


def matheus_solution(info, **kwargs):
    # TODO write your solution here!
    M, T2, T3, T4, pizzas = info

    # TODO decide number of choices and do without replacement
    pizza_idxs = np.array([i for i in range(len(pizzas))])

    new_pizzas = []
    for i, val in enumerate(pizzas):
        new_pizzas.append(Pizza(val, i))

    sorted_new_pizzas = sorted(new_pizzas, key=operator.attrgetter('score'), reverse=True)
    
    # np.random.shuffle(pizza_idxs)

    draw_arr = []
    for i in range(T2):
        draw_arr.append(2)
    for i in range(T3):
        draw_arr.append(3)
    for i in range(T4):
        draw_arr.append(4)
    solution = []

    curr_idx = 0
    for val in draw_arr:
        end_idx = curr_idx + val
        if end_idx <= len(sorted_new_pizzas):
            choices = [ n.idx for n in sorted_new_pizzas[curr_idx:end_idx]]
            team_size = val
            new_entry = [team_size,] + choices
            solution.append(new_entry)
        curr_idx += val

    # TODO Parse any parameters you need
    val1 = kwargs.get("name", None)

    score = scorer(solution, info)
    return solution, score
