# Use this to test something in particular
from time import time

from solution import print_solution
from sean import sean_solution


def test_method(method, info, **kwargs):
    """Can be used to test a method with particular values."""
    start_time = time()
    solution = method(info, **kwargs)
    print("\tCompleted in {} seconds".format(time() - start_time))
    print_solution(solution)


if __name__ == "__main__":
    info = []
    test_method(sean_solution, info)
