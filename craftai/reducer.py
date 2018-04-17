from functools import reduce

from .errors import CraftAiError
from .formatters import format_decision_rule
from .operators import OPERATORS

def _is_is_reducer(rule_1, rule_2):
  if rule_1["operand"] and (rule_1["operand"] != rule_2["operand"]):
    raise CraftAiError("Operator '{}' can't have different value. Set to '{}' and receive '{}'"
                       .format(OPERATORS["IS"], rule_1["operand"], rule_2["operand"]))
  return {
    "operator": OPERATORS["IS"],
    "operand": rule_2["operand"]
  }

def _in_in_reducer(rule_1, rule_2):
  op_1_from = rule_1["operand"][0]
  op_1_to = rule_1["operand"][1]

  op_2_from = rule_2["operand"][0]
  op_2_to = rule_2["operand"][1]

  op_1_is_cyclic = op_1_from > op_1_to
  op_2_is_cyclic = op_2_from > op_2_to
  op_2_from_in_op_1 = ((op_2_from >= op_1_from or op_2_from <= op_1_to) if op_1_is_cyclic
                       else (op_2_from >= op_1_from and op_2_from <= op_1_to))
  op_2_to_in_op_1 = ((op_2_to >= op_1_from or op_2_to <= op_1_to) if op_1_is_cyclic
                     else (op_2_to >= op_1_from and op_2_to <= op_1_to))
  op_1_from_in_op_2 = ((op_1_from >= op_2_from or op_1_from <= op_2_to) if op_2_is_cyclic
                       else (op_1_from >= op_2_from and op_1_from <= op_2_to))
  op_1_to_in_op_2 = ((op_1_to >= op_2_from or op_1_to <= op_2_to) if op_2_is_cyclic
                     else (op_1_to >= op_2_from and op_1_to <= op_2_to))

  if op_1_from_in_op_2 and op_1_to_in_op_2:
    # op_1 belongs to op_2
    #    |    op_1    |
    #   |       op_2       |
    return rule_1

  if op_2_from_in_op_1 and op_2_to_in_op_1:
    # op_2 belongs to op_1
    #    |    op_1    |
    #      |  op_2  |
    return rule_2

  if op_2_from_in_op_1 and op_1_to_in_op_2:
    # overlap 1
    #    |    op_1    |
    #             |   op_2   |
    return {
      "operator": OPERATORS["IN"],
      "operand": [op_2_from, op_1_to]
    }

  if op_2_to_in_op_1 and op_1_from_in_op_2:
    # overlap 2
    #        |    op_1    |
    #     |   op_2   |
    return {
      "operator": OPERATORS["IN"],
      "operand": [op_1_from, op_2_to]
    }

  # disjointed
  #    |    op_1    |
  #                  |   op_2   |
  raise CraftAiError("""Unable to reduce decision rules '{}' and '{}': """
                     """the resulting rule is not fulfillable."""
                     .format(format_decision_rule(rule_1), format_decision_rule(rule_2)))

def _in_gte_reducer(rule_1, rule_2):
  op_1_from = rule_1["operand"][0]
  op_1_to = rule_1["operand"][1]
  op_2 = rule_2["operand"]

  op_1_is_cyclic = op_1_from > op_1_to

  if op_1_is_cyclic:
    # Cyclics makes no sense with single bound limits
    raise CraftAiError("""Unable to reduce decision rules '{}' and '{}': """
                       """the resulting rule is not fulfillable."""
                       .format(format_decision_rule(rule_1), format_decision_rule(rule_2)))

  if op_2 >= op_1_to:
    # op_2 after op_1, disjointed
    #    |    op_1    |
    #                  |op_2
    raise CraftAiError("""Unable to reduce decision rules '{}' and '{}': """
                       """the resulting rule is not fulfillable."""
                       .format(format_decision_rule(rule_1), format_decision_rule(rule_2)))

  if op_2 >= op_1_from and op_2 < op_1_to:
    # op_2 belongs to op_1
    #    |    op_1    |
    #           |op_2
    return {
      "operator": OPERATORS["IN"],
      "operand": [op_2, op_1_to]
    }

  # op_2 before op_1
  #    |    op_1    |
  #   |op_2
  return rule_1

def _in_lt_reducer(rule_1, rule_2):
  op_1_from = rule_1["operand"][0]
  op_1_to = rule_1["operand"][1]
  op_2 = rule_2["operand"]

  op_1_is_cyclic = op_1_from > op_1_to

  if op_1_is_cyclic:
    # Cyclics makes no sense with single bound limits
    raise CraftAiError("""Unable to reduce decision rules '{}' and '{}': """
                       """the resulting rule is not fulfillable."""
                       .format(format_decision_rule(rule_1), format_decision_rule(rule_2)))

  if op_2 < op_1_from:
    # op_2 before op_1, disjointed
    #      |    op_1    |
    # op_2|
    raise CraftAiError("""Unable to reduce decision rules '{}' and '{}': """
                       """the resulting rule is not fulfillable."""
                       .format(format_decision_rule(rule_1), format_decision_rule(rule_2)))

  if op_2 >= op_1_from and op_2 < op_1_to:
    # op_2 belongs to op_1
    #    |    op_1    |
    #           |op_2
    return {
      "operator": OPERATORS["IN"],
      "operand": [op_1_from, op_2]
    }

  # op_2 after op_1
  #    |    op_1    |
  #                 op_2|
  return rule_1

def _gte_lt_reducer(rule_1, rule_2):
  new_lower_bound = rule_1["operand"]
  new_upper_bound = rule_2["operand"]
  if new_upper_bound < new_lower_bound:
    raise CraftAiError("""Unable to reduce decision rules '{}' and '{}': """
                       """the resulting rule is not fulfillable."""
                       .format(format_decision_rule(rule_1), format_decision_rule(rule_2)))
  return {
    "operator": OPERATORS["IN"],
    "operand": [new_lower_bound, new_upper_bound]
  }

REDUCER_FROM_DECISION_RULE = {
  OPERATORS["IS"]: {
    OPERATORS["IS"]: _is_is_reducer
  },
  OPERATORS["IN"]: {
    OPERATORS["IN"]: _in_in_reducer,
    OPERATORS["GTE"]: _in_gte_reducer,
    OPERATORS["LT"]: _in_lt_reducer
  },
  OPERATORS["GTE"]: {
    OPERATORS["IN"]: lambda rule_1, rule_2: _in_gte_reducer(rule_2, rule_1),
    OPERATORS["GTE"]: lambda rule_1, rule_2: {
      "operator": OPERATORS["GTE"],
      "operand": max(rule_1["operand"], rule_2["operand"])
    },
    OPERATORS["LT"]: _gte_lt_reducer
  },
  OPERATORS["LT"]: {
    OPERATORS["IN"]: lambda rule_1, rule_2: _in_lt_reducer(rule_2, rule_1),
    OPERATORS["GTE"]: lambda rule_1, rule_2: _gte_lt_reducer(rule_2, rule_1),
    OPERATORS["LT"]: lambda rule_1, rule_2: {
      "operator": OPERATORS["LT"],
      "operand": min(rule_1["operand"], rule_2["operand"])
    }
  }
}

def _decision_rules_reducer(rule_1, rule_2):
  if rule_1 is None or rule_2 is None:
    return rule_1 if rule_1 is not None else rule_2
  if (rule_1["operator"] not in REDUCER_FROM_DECISION_RULE or
      rule_2["operator"] not in REDUCER_FROM_DECISION_RULE[rule_1["operator"]]):
    raise CraftAiError("""Unable to reduce decision rules '{}' and '{}': """
                       """incompatible operators."""
                       .format(format_decision_rule(rule_1), format_decision_rule(rule_2)))
  return REDUCER_FROM_DECISION_RULE[rule_1["operator"]][rule_2["operator"]](rule_1, rule_2)

def reduce_decision_rules(rules):
  return reduce(_decision_rules_reducer, rules)
