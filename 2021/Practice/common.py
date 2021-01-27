"""Please place things here which may be useful to everyone."""


def scorer(solution, input_info):
    """Return the square of the total number of different ingredients in the pizzas."""
    # TODO process the solution
    # Essentially map the pizzas to ingredients
    _, _, _, _, input_pizzas = input_info

    # One line in solution is
    # team_members, pizzas = line[0], line[1:]

    pizzas = []
    for line in solution:
        line = line[1:]
        new_entry = []
        for idx in line:
            new_entry += input_pizzas[idx]
        pizzas.append(new_entry)

    # def map_fn(pizza_numbers):
    #     out_arr = []
    #     for num in pizza_numbers:
    #         out_arr = out_arr + input_pizzas[num]
    #     return out_arr

    # output_pizzas = [line[1:] for line in solution]
    # pizzas = map(map_fn, output_pizzas)

    # Do the actual squared sum
    scores = [len(set(pizza)) ** 2 for pizza in pizzas]
    return sum(scores)
