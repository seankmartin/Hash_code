# Use this to test something in particular
from time import time
import os
import pickle

from solution import print_solution
from sean import sean_solution
from hyperopt import Trials


def test_method(method, info, **kwargs):
    """Can be used to test a method with particular values."""
    start_time = time()
    solution = method(info, **kwargs)
    print("\tCompleted in {} seconds".format(time() - start_time))
    print_solution(solution)


def print_trials(in_dir):
    for f in os.listdir(in_dir):
        if f[-3:] == "pkl":
            with open(os.path.join(in_dir, f), "rb") as inp:
                trial = pickle.load(inp)
                print("For {}:".format(f))
                for d, l in zip(trial.trials, trial.losses()):
                    print("\t{}: Loss {}".format(d["misc"]["vals"], l))


if __name__ == "__main__":
    # info = []
    # test_method(sean_solution, info)
    here = os.path.dirname(os.path.realpath(__file__))
    dirname = "01-02-46"
    in_dir = os.path.join(here, "outputs", dirname)
    print_trials(in_dir)
