def _flatten(arr, flat=[]):
  """ flatten deep an array of lists """
  [flat.append(a) for a in arr if type(a) != list]
  return _flatten([x for y in arr for x in y if type(y)==list], flat) if sum([type(a) == list for a in arr]) > 0 else flat

def _update_paths(p, idx):
  """ add new path build on idx to all paths """
  return p + [f'{p[-1]}-{idx}'] if len(p) > 0 else [f'{idx}']

def _paths(t, paths=['0']):
  """ return a raw list of all paths in a tree """
  return [_paths(c, _update_paths(paths, idx)) for idx, c in enumerate(t['children'])] if 'children' in t.keys() else paths

def _get_paths(tree):
  """ return a set of all paths in a tree """
  return set(_flatten(_paths(tree)))

def _is_neightbour(p0, p1):
  """
  Boolean function. a neightbour has exactly the same path excepted for the last node
  """
  return p0[:-1]==p1[:-1] and p0!=p1

def _get_neightbours(paths, dp):
  """
  Recursively collect all neightbours paths of the given decision path
  param: paths: paths aggregator
  param: dp: decision path
  """
  split = dp.split('-')
  return [p for p in paths for i in range(1, len(split)) if _is_neightbour(p, '-'.join(split[:i]))]

def _extract_tree(tree):
  target = list(tree['trees'].keys())[0]
  return tree['trees'][target]