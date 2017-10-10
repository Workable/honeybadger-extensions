def csv_to_list(value):
    """
    Converts the given value to a list of strings, spliting by ',' and removing empty strings.
    :param str value: the value to split to strings.
    :return: a list of strings.
    :rtype: List[str]
    """
    return list(filter(None, [x.strip() for x in value.split(',')]))
