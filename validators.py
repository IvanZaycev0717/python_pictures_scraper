def is_saving_path_given(path: str) -> bool:
    """
    Checks if a saving path is given.

    >>> is_saving_path_given('/path/to/save/file.txt')
    True
    >>> is_saving_path_given('')
    False
    >>> is_saving_path_given(None)
    False
    """
    return bool(path)


def is_pictures_amount_chosen(pictures_amount: int) -> bool:
    """
    Checks if a number of pictures has been chosen.

    >>> is_pictures_amount_chosen(5)
    True
    >>> is_pictures_amount_chosen(0)
    False
    >>> is_pictures_amount_chosen(-1)
    True
    """
    return bool(pictures_amount)


def is_pictures_amount_positive_int(pictures_amount: int) -> bool:
    """
    Checks if the number of pictures is a positive integer.

    >>> is_pictures_amount_positive_int(5)
    True
    >>> is_pictures_amount_positive_int(0)
    False
    >>> is_pictures_amount_positive_int(-1)
    False
    """
    return pictures_amount > 0


def is_picture_amount_correct(pictures_amount: int,
                              links_array: set[str]) -> bool:
    """
    Checks if the number of pictures is correct
    based on the number of links in the array.

    >>> is_picture_amount_correct(3, {'link1', 'link2', 'link3'})
    True
    >>> is_picture_amount_correct(5, {'link1', 'link2', 'link3'})
    False
    >>> is_picture_amount_correct(0, {'link1', 'link2', 'link3'})
    True
    """
    return pictures_amount <= len(links_array)
