import os
import time
import itertools
import math

import numpy as np

# In case doing hyperparam opt
try:
    from hyperopt import fmin, tpe, hp, STATUS_OK, Trials, space_eval
except:
    pass

from utils import save_object
from common import scorer

# TODO Put classes here that may be useful to store info in


class General:
    """
    These is a template for a general class with some
    things which can be useful.
    """

    def __init__(self, args, idx):
        self.score = 0
        self.idx = idx

    def __repr__(self):
        return "Thing {} with properties".format(self.idx)


def sean_solution(info, **kwargs):
    """
    This solution is designed to be performed as follows:
    1.  Setup anything, such as arrays or sorting.
        Also break down info into components.
    2.  objective can access anything from the main body part.
        As such, pass anything extra which may be needed
        (such as hyper-params) into objective as args (a dict)
        perform the actual solving logic part here.
    3.  At the end, can search over hyper-paramters (the args)
        That are passed into objective.
        However, if doing a simple function, this part
        can be safely ignored.

    """
    # TODO main body part here - especially setup

    def objective(args):
        """Actually write the solution part here."""
        # TODO Parse out the args if needed
        val = args.get(["name", None])

        # TODO Solve the thing here
        solution = 0
        score = 0

        # Return something flexible that can be used with hyperopt
        # Main point is that it has score and solution.
        return {
            "loss": -score,
            "score": score,
            "solution": solution,
            "eval_time": time.time(),
            "status": STATUS_OK,
        }

    # Ignore this bit if not searching hyper_parameters!
    if kwargs.get("search", True):
        trials = Trials()

        # TODO Setup what values the args searching over can have
        space = hp.choice(
            "args",
            [{"arg1": hp.lognormal("arg1", 1, 0.5), "arg2": hp.uniform("arg2", 1, 10)}],
        )

        # TODO If you know the best you do, pass loss_threshold=-best
        # Do hyper-param searching - possible pass per filename num_evals
        best = fmin(
            objective,
            space=space,
            algo=tpe.suggest,
            max_evals=kwargs.get("num_evals", 10),
            trials=trials,
        )

        # Get the best hyper-params from fmin
        print("Best hyper-parameters found were:", best)
        args = space_eval(space, best)

        # Save the trials to disk
        # These trials can be printed using print_trial_info in utils
        out_name = os.path.join(
            kwargs["output_dir"], "_" + kwargs["input_name"][:-2] + "pkl"
        )
        save_object(trials, out_name)

    else:
        # By default, this is just an empty dictionary.
        args = kwargs.get("objective_args")

    result = objective(args)
    return result["solution"], result["score"]


def assign_pizzas(sorted_pizzas, draw_arr, info):
    solution = []
    curr_idx = 0
    for val in draw_arr:
        end_idx = curr_idx + val
        if end_idx <= len(sorted_pizzas):
            choices = [n for n in sorted_pizzas[curr_idx:end_idx]]
            team_size = val
            new_entry = [team_size,] + choices
            solution.append(new_entry)
        curr_idx += val

    score = scorer(solution, info)

    return solution, score


def make_draw_arr(total_pizzas, order, size_dict):
    total_used = 0
    draw_arr = []
    for val in order:
        team_size = size_dict[val]
        for i in range(team_size):
            if total_used + val <= total_pizzas:
                draw_arr.append(val)
                total_used += val
            else:
                break
    return draw_arr


def brute_force(info, **kwargs):
    """Brute force best solution - should only be used on the first."""
    M, T2, T3, T4, pizzas = info

    pizza_idxs = [i for i in range(len(pizzas))]

    # Can order as T2 > T3 > T4 and permutes
    teams = [2, 3, 4]
    team_dict = {2: T2, 3: T3, 4: T4}

    total_possible = 0
    best_score = 0

    # team_permutations = 6
    # pizza_permutations = math.factorial(M)
    for team_perm in itertools.permutations(teams):
        draw_arr = make_draw_arr(M, team_perm, team_dict)
        for i, pizza_perm in enumerate(itertools.permutations(pizza_idxs)):
            solution, score = assign_pizzas(pizza_perm, draw_arr, info)
            if score > best_score:
                best_solution = solution
                best_score = score
            total_possible += 1

    print("Tested a total of {} solutions".format(total_possible))
    print("The best solution was {}".format(best_solution))
    return best_solution, best_score
