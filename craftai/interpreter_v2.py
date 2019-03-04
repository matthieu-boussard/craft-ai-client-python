import numbers
import six

from craftai.errors import CraftAiDecisionError, CraftAiNullDecisionError
from craftai.operators import OPERATORS, OPERATORS_FUNCTION
from craftai.types import TYPES
from craftai.timezones import is_timezone

_DECISION_VERSION = "2.0.0"

_VALUE_VALIDATORS = {
  TYPES["continuous"]: lambda value: isinstance(value, numbers.Real),
  TYPES["enum"]: lambda value: isinstance(value, six.string_types),
  TYPES["boolean"]: lambda value: isinstance(value, bool),
  TYPES["timezone"]: lambda value: is_timezone(value),
  TYPES["time_of_day"]: lambda value: (isinstance(value, numbers.Real)
                                       and value >= 0 and value < 24),
  TYPES["day_of_week"]: lambda value: (isinstance(value, six.integer_types)
                                       and value >= 0 and value <= 6),
  TYPES["day_of_month"]: lambda value: (isinstance(value, six.integer_types)
                                        and value >= 1 and value <= 31),
  TYPES["month_of_year"]: lambda value: (isinstance(value, six.integer_types)
                                         and value >= 1 and value <= 12)
}

##############################
## Interpreter for V2 Trees ##
##############################

class InterpreterV2(object):

  @staticmethod
  def decide(configuration, bare_tree, context):
    # Check if missing values are handled
    deactivate_missing_values = True
    if configuration.get("deactivate_missing_values", True) is False:
      deactivate_missing_values = False

    InterpreterV2._check_context(configuration, context, deactivate_missing_values)

    decision_result = {}
    decision_result["output"] = {}
    for output in configuration.get("output"):
      output_type = configuration["context"][output]["type"]
      decision_result["output"][output] = InterpreterV2._decide_recursion(bare_tree[output],
                                                                          context,
                                                                          bare_tree[output].get(
                                                                            "output_values"),
                                                                          output_type,
                                                                          deactivate_missing_values)
    decision_result["_version"] = _DECISION_VERSION
    return decision_result

  @staticmethod
  def _decide_recursion(node, context, output_values, output_type, deactivate_missing_values):
    # If we are on a leaf
    if not (node.get("children") is not None and len(node.get("children"))):
      # We check if a leaf has the key 'prediction' corresponging to a v2 tree
      prediction = node.get("prediction")
      if prediction is None:
        prediction = node

      predicted_value = prediction.get("value")
      if predicted_value is None:
        raise CraftAiNullDecisionError(
          """Unable to take decision: the decision tree has no valid"""
          """ predicted value for the given context."""
        )

      leaf = {
        "predicted_value": predicted_value,
        "confidence": prediction.get("confidence") or 0,
        "decision_rules": [],
        "nb_samples": prediction["nb_samples"]
      }

      distribution = prediction.get("distribution")
      if not isinstance(distribution, list) and distribution.get("standard_deviation"):
        leaf["standard_deviation"] = distribution.get("standard_deviation")
        leaf["min"] = distribution.get("min")
        leaf["max"] = distribution.get("max")
      else:
        leaf["distribution"] = distribution

      return leaf
    # Finding the first element in this node's childrens matching the
    # operator condition with given context
    matching_child = InterpreterV2._find_matching_child(node, context, deactivate_missing_values)

    # If there is no child corresponding matching the operators then we compute
    # the probabilistic distribution from this node.
    if not matching_child:
      if not deactivate_missing_values:
        return InterpreterV2.compute_distribution(node, output_values, output_type)
      prop = node.get("children")[0].get("decision_rule").get("property")
      raise CraftAiNullDecisionError(
        """Unable to take decision: value '{}' for property '{}' doesn't"""
        """ validate any of the decision rules.""".format(context.get(prop), prop)
        )

    # If a matching child is found, recurse
    result = InterpreterV2._decide_recursion(matching_child, context, output_values,
                                             output_type, deactivate_missing_values)
    new_predicates = [{
      "property": matching_child["decision_rule"]["property"],
      "operator": matching_child["decision_rule"]["operator"],
      "operand": matching_child["decision_rule"]["operand"]
    }]

    final_result = {
      "predicted_value": result["predicted_value"],
      "confidence": result["confidence"],
      "decision_rules": new_predicates + result["decision_rules"],
      "nb_samples": result["nb_samples"],
    }

    if result.get("standard_deviation", None) is not None:
      final_result["standard_deviation"] = result.get("standard_deviation")

    if result.get("min") is not None:
      final_result["min"] = result.get("min")

    if result.get("max") is not None:
      final_result["max"] = result.get("max")

    if result.get("distribution"):
      final_result["distribution"] = result.get("distribution")

    return final_result

  @staticmethod
  def compute_distribution(node, output_values, output_type):
    result, size = InterpreterV2._distribution(node)
    if output_type == "enum":
      final_result = {
        "predicted_value": output_values[result.index(max(result))],
        "distribution": result
      }
    else:
      final_result = {"predicted_value": result}
    final_result["decision_rules"] = []
    final_result["confidence"] = None
    final_result["nb_samples"] = size
    return final_result

  @staticmethod
  def _distribution(node):
    # If it is a leaf
    if not (node.get("children") is not None and len(node.get("children"))):
      prediction = node["prediction"]
      value_distribution = prediction["distribution"]
      nb_samples = prediction["nb_samples"]
      # It is a classification problem
      if isinstance(value_distribution, list):
        return [value_distribution, nb_samples]

      # It is a regression problem
      predicted_value = prediction.get("value")
      if predicted_value is not None:
        return [predicted_value, nb_samples]

      raise CraftAiDecisionError(
        """Unable to take decision: the decision tree has no valid"""
        """ predicted value for the given context."""
      )

    # If it is not a leaf, we recurse into the children and store
    # the distributions/means and sizes of each child branch.
    def recurse(_child):
      return InterpreterV2._distribution(_child)
    values_sizes = map(recurse, node.get("children"))
    values, sizes = zip(*values_sizes)
    if isinstance(values[0], list):
      return InterpreterV2.compute_mean_distributions(values, sizes)
    return InterpreterV2.compute_mean_values(values, sizes)

  @staticmethod
  def compute_mean_distributions(values, sizes):
    # Compute the weighted mean of the given array of distributions (array of probabilities).
    # Example, for values = [[ 4, 3, 6 ], [1, 2, 3], [3, 4, 5]], sizes = [1, 2, 1]
    # This function computes ([ 4, 3, 6]*1 + [1, 2, 3]*2 + [3, 4, 5]*6) / (1+2+1) = ...
    total_size = sum(sizes)
    ratio_applied = [[x * size / float(total_size) for x in x_array]
                     for x_array, size in zip(values, sizes)]
    return list(map(sum, zip(*ratio_applied))), total_size

  @staticmethod
  def compute_mean_values(values, sizes):
    # Compute the weighted mean of the given array of values.
    # Example, for values = [ 4, 3, 6 ], sizes = [1, 2, 1]
    # This function computes (4*1 + 3*2 + 1*6) / (1+2+1) = 16/4 = 4
    total_size = sum(sizes)
    mean = sum([val * size / float(total_size)
                for val, size in zip(values, sizes)])
    return mean, total_size

  @staticmethod
  def _find_matching_child(node, context, deactivate_missing_values=True):
    for child in node["children"]:
      property_name = child["decision_rule"]["property"]
      operand = child["decision_rule"]["operand"]
      operator = child["decision_rule"]["operator"]
      context_value = context.get(property_name)

      # If there is no context value:
      if context_value is None:
        if deactivate_missing_values:
          raise CraftAiDecisionError(
            """Unable to take decision, property '{}' is missing from the given context.""".
            format(property_name)
          )
      if (not isinstance(operator, six.string_types) or
          not operator in OPERATORS.values()):
        raise CraftAiDecisionError(
          """Invalid decision tree format, {} is not a valid"""
          """ decision operator.""".format(operator)
        )

      if OPERATORS_FUNCTION[operator](context_value, operand):
        return child
    return {}

  @staticmethod
  def _check_context(configuration, context, deactivate_missing_values=True):
    # Extract the required properties (i.e. those that are not the output)
    expected_properties = [
      p for p in configuration["context"]
      if not p in configuration["output"]
    ]

    if deactivate_missing_values:
      # Retrieve the missing properties
      missing_properties = [
        p for p in expected_properties
        if not p in context or context[p] is None
      ]
    else:
      missing_properties = []

    # Validate the values
    bad_properties = [
      p for p in expected_properties
      if not InterpreterV2.validate_property_value(configuration, context, p)
    ]
    if missing_properties or bad_properties:
      missing_properties = sorted(missing_properties)
      missing_properties_messages = [
        "expected property '{}' is not defined"
        .format(p) for p in missing_properties
      ]
      bad_properties = sorted(bad_properties)
      bad_properties_messages = [
        "'{}' is not a valid value for property '{}' of type '{}'"
        .format(context[p], p, configuration["context"][p]["type"]) for p in bad_properties
      ]

      errors = missing_properties_messages + bad_properties_messages

      # deal with missing properties
      if errors:
        message = "Unable to take decision, the given context is not valid: " + errors.pop(0)

        for error in errors:
          message = "".join((message, ", ", error))
        message = message + "."

        raise CraftAiDecisionError(message)

  @staticmethod
  def validate_property_value(configuration, context, property_name):
    if not property_name in context:
      return False

    if context[property_name] is None:
      return True
    property_def = configuration["context"][property_name]
    property_type = property_def["type"]
    is_optional = property_def.get("is_optional")
    if property_type in _VALUE_VALIDATORS:
      property_value = context[property_name]
      return _VALUE_VALIDATORS[property_type](property_value) or (is_optional
                                                                  and property_value == {})
    return True
