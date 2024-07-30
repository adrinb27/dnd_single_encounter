#TODO create a helper class

def create_string_from_dict_attributes(dict):
  """Creates a string out of the attributes of a dictionary.

  Args:
    dict: The dictionary to convert to a string.

  Returns:
    A string containing the attributes of the dictionary.
  """

  string = ""
  last = list(dict.keys())[-1]
  for key in list(dict.keys()):
    if key == last:
      string += f"and {key}. "
    else:
        string += f"{key}, "
  return string

def transform(array):
    new_dict = {}
    for item in array:
        name = item['name']
        new_dict[name] = item
    return new_dict