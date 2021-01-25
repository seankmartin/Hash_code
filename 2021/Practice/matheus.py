# TODO import your packages
import numpy as np

from common import scorer


def matheus_solution(info, **kwargs):
    # TODO write your solution here!
    M, T2, T3, T4, pizzas = info

    # TODO decide number of choices and do without replacement
    pizza_idxs = np.array([i for i in range(len(pizzas))])
    
    np.random.shuffle(pizza_idxs)
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
        if end_idx <= len(pizzas):
            choices = list(pizza_idxs[curr_idx:end_idx])
            team_size = val
            new_entry = [team_size,] + choices
            solution.append(new_entry)
        curr_idx += val

    # TODO Parse any parameters you need
    val1 = kwargs.get("name", None)

    score = scorer(solution, info)
    return solution, score
