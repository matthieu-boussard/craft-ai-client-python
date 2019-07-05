import pandas as pd

from .. import Interpreter as VanillaInterpreter, Time
from ..errors import CraftAiNullDecisionError
from .utils import is_valid_property_value, create_timezone_df, DUMMY_COLUMN_NAME, format_input

def decide_from_row(tree, row, tz_col):
  context = {
    index: format_input(value) for index, value in row.iteritems()
    if is_valid_property_value(index, value)
  }
  time = Time(
    t=row.name.value // 1_000_000_000, # Timestamp.value returns nanoseconds
    timezone=row[tz_col] if tz_col else row.name.tz
  )
  try:
    decision = VanillaInterpreter.decide(tree, [context, time])

    return {
      f"{output}_{key}": value
      for output, output_decision in decision["output"].items()
      for key, value in output_decision.items()
    }
  except CraftAiNullDecisionError as e:
    return {"error": e.message}

class Interpreter(VanillaInterpreter):
  @staticmethod
  def decide_from_contexts_df(tree, contexts_df):
    _, configuration, _ = VanillaInterpreter._parse_tree(tree)
    df = contexts_df.copy(deep=True)

    tz_col = [key for key, value in configuration["context"].items()
              if value["type"] == "timezone"]
    if tz_col:
      tz_col = tz_col[0]
    # If a timezone is needed create a timezone dataframe which will
    # store the timezone to use. It can either be the DatetimeIndex
    # timezone or the timezone column if provided.
    if tz_col:
      df[tz_col] = create_timezone_df(df, tz_col).iloc[:, 0]

    l_predictions = []
    for _, row in df.iterrows():
      prediction = decide_from_row(tree, row, tz_col)
      l_predictions.append(prediction)
    predictions_df = pd.DataFrame(l_predictions, index=df.index)

    return predictions_df
