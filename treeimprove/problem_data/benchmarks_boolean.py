def objective_func_cmpV(input_pattern, num_bits):
    """This is the objective function for 
    the Cmp6 benchmark.

    :param input_pattern: A list of fitness tests.
    :returns: The target output for each input fitness tests.
    """

    input_pattern = [str(int(elem)) for elem in input_pattern]
    input_pattern = ''.join(input_pattern)

    split_point = int(len(input_pattern)/2.)

    most_sig_bits = input_pattern[:split_point]
    least_sig_bits = input_pattern[split_point:]

    most_sig_val = int(most_sig_bits, 2)
    least_sig_val = int(least_sig_bits, 2)

    if least_sig_val < most_sig_val:
        return 1

    return 0

def objective_func_muxV(input_pattern, num_bits):
    '''
    This is the objective function for MuxV.
    '''

    if num_bits == 6:

        [s1, s2] = input_pattern[:2]
        s1, s2 = int(s1), int(s2)

        if s1 == 0 and s2 == 0:
            return int(input_pattern[2])

        elif s1 == 1 and s2 == 0:
            return int(input_pattern[3])

        elif s1 == 0 and s2 == 1:
            return int(input_pattern[4])

        elif s1 == 1 and s2 == 1:
            return int(input_pattern[5])

    elif num_bits == 11:

        [s1, s2, s3] = input_pattern[:3]
        s1, s2, s3 = int(s1), int(s2), int(s3)

        if (s1, s2, s3) == (0, 0, 0):
            return int(input_pattern[3])

        elif (s1, s2, s3) == (0, 0, 1):
            return int(input_pattern[4])

        elif (s1, s2, s3) == (0, 1, 0):
            return int(input_pattern[5])

        elif (s1, s2, s3) == (1, 0, 0):
            return int(input_pattern[6])

        elif (s1, s2, s3) == (0, 1, 1):
            return int(input_pattern[7])

        elif (s1, s2, s3) == (1, 0, 1):
            return int(input_pattern[8])

        elif (s1, s2, s3) == (1, 1, 0):
            return int(input_pattern[9])

        elif (s1, s2, s3) == (1, 1, 1):
            return int(input_pattern[10])

    elif num_bits == 20:

        [s1, s2, s3, s4] = input_pattern[:4]
        s1, s2, s3, s4 = int(s1), int(s2), int(s3), int(s4)

        if (s1, s2, s3, s4) == (0, 0, 0, 0):
            return int(input_pattern[4])

        elif (s1, s2, s3, s4) == (0, 0, 0, 1):
            return int(input_pattern[5])

        elif (s1, s2, s3, s4) == (0, 0, 1, 0):
            return int(input_pattern[6])

        elif (s1, s2, s3, s4) == (0, 0, 1, 1):
            return int(input_pattern[7])

        elif (s1, s2, s3, s4) == (0, 1, 0, 0):
            return int(input_pattern[8])

        elif (s1, s2, s3, s4) == (0, 1, 0, 1):
            return int(input_pattern[9])

        elif (s1, s2, s3, s4) == (0, 1, 1, 0):
            return int(input_pattern[10])

        elif (s1, s2, s3, s4) == (0, 1, 1, 1):
            return int(input_pattern[11])

        elif (s1, s2, s3, s4) == (1, 0, 0, 0):
            return int(input_pattern[12])

        elif (s1, s2, s3, s4) == (1, 0, 0, 1):
            return int(input_pattern[13])

        elif (s1, s2, s3, s4) == (1, 0, 1, 0):
            return int(input_pattern[14])

        elif (s1, s2, s3, s4) == (1, 0, 1, 1):
            return int(input_pattern[15])

        elif (s1, s2, s3, s4) == (1, 1, 0, 0):
            return int(input_pattern[16])

        elif (s1, s2, s3, s4) == (1, 1, 0, 1):
            return int(input_pattern[17])

        elif (s1, s2, s3, s4) == (1, 1, 1, 0):
            return int(input_pattern[18])

        elif (s1, s2, s3, s4) == (1, 1, 1, 1):
            return int(input_pattern[19])

    else:
        print('ERROR objective_func_muxV: number of bits incorrect, must be 6 or 11')
        exit()

def objective_func_majV(input_pattern, num_bits):
    '''
    This is the objective function for MajV.
    '''

    # count number of 1's
    count_ones = 0
    for i in input_pattern:
        if i == 1:
            count_ones += 1

    # return true if more than half the bits are true
    if count_ones > int(num_bits/2.):
        return 1
    else:
        return 0

def objective_func_parV(input_pattern, num_bits):
    '''
    This is the objective function for ParV.
    '''

    # count number of 1's
    count_ones = 0
    for i in input_pattern:
        if i == 1:
            count_ones += 1

    if count_ones % 2 != 0:
        # odd number of true inputs, so return true
        return 1
    else:
        return 0

def objective_func_muxVparV(input_pattern, num_bits):
    """Experimental complicated benchmark, a mix of mux and par."""
    muxV = objective_func_muxV(input_pattern, num_bits)
    parV = objective_func_parV(input_pattern, num_bits)

    if (muxV == 1) and (parV == 1):
        # odd number of true inputs, so return true
        return 1
    else:
        return 0