def convert_dict_to_tuple(d):
    """
    Converts an unhashable dict to a hashable tuple, sorted by key.
    """
    return tuple(sorted(d.items(), key=lambda item: item[0]))
