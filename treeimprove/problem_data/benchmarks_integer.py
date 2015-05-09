def objective_func_discrim(input_pattern):
    """This is the objective function for the catagorical
    discriminator term.

    :param input_pattern: A single fitness test with three values.
    :returns: The target output for the fitness test.
    """

    x, y, z = input_pattern

    if x != y:
        return x
    elif x == y:
        return z

    print('ERROR objective_func_discrim')
    exit()

def objective_func_malcev(input_pattern):
    """This is the objective function for the catagorical
    Mal'cev term.

    :param input_pattern: A single fitness test with three values.
    :returns: The target output for the fitness test.
    """

    if input_pattern[0] == input_pattern[1]:
        return input_pattern[2]

    elif input_pattern[1] == input_pattern[2]:
        return input_pattern[0]

    print('ERROR objective_func_malcev')
    exit()