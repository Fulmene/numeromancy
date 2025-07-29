def transpose(m): # Transpose a list of list or any similar data structures
    return [list(m) for m in zip(*m)]
