import os

def encoding_categories(categories):
    categories = list(set(categories))
    categories.sort()
    strs = [str(i) + "-" for i in categories]
    res = "".join(strs)
    res = res[:-1]
    return res

def decoding_categories(category_str):
    categories = category_str.split("-")
    categories = [int(i) for i in categories]
    return categories