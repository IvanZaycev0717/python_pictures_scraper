def is_saving_path_given(path):
    return bool(path)

def is_pictures_amount_chosen(pictures_amount):
    return bool(pictures_amount)

def is_pictures_amount_positive_int(pictures_amount):
    return pictures_amount > 0

def is_picture_amount_correct(pictures_amount, links_array):
    return pictures_amount <= len(links_array)