from math import sqrt
from nose.tools import assert_equal, assert_true
from craft_ai.interpreter_v2 import InterpreterV2

def test_regression_mean():
  means = [10, 20, 30]
  sizes = [1, 1, 1]
  res = list(InterpreterV2.compute_mean_values(means, sizes))
  assert_equal(res, [20.0, 3])

  means = [10, 20, 30]
  sizes = [0, 0, 1000]
  res = list(InterpreterV2.compute_mean_values(means, sizes))
  assert_equal(res, [30.0, 1000])

def test_regression_mean_std():
  means = [4, 5]
  stds = [1.0, 2.0]
  sizes = [3, 5]
  mean, size, std = list(InterpreterV2.compute_mean_values(means, sizes, stds))
  assert_equal(mean, 37.0 / 8.0)
  assert_equal(size, 8.0)
  assert_true(abs((std - sqrt((18.0 + 15.0 / 8.0) / 7.0))) < 0.001)

  means = [0, 5]
  stds = [0, 2]
  sizes = [0, 5]
  mean, size, std = list(InterpreterV2.compute_mean_values(means, sizes, stds))
  assert_equal(mean, 5.0)
  assert_equal(size, 5.0)
  assert_true(abs((std - 2.0)) < 0.001)

  means = [5, 0]
  stds = [2, 0]
  sizes = [5, 0]
  mean, size, std = list(InterpreterV2.compute_mean_values(means, sizes, stds))
  assert_equal(mean, 5.0)
  assert_equal(size, 5.0)
  assert_true(abs((std - 2.0)) < 0.001)

  means = [1, 5]
  stds = [15, 2]
  sizes = [1, 5]
  mean, size, std = list(InterpreterV2.compute_mean_values(means, sizes, stds))
  assert_equal(mean, 26.0 / 6.0,)
  assert_equal(size, 6.0)
  assert_true(abs((std - sqrt((16.0 + 80.0 / 6.0) / 5.0))) < 0.001)

  means = [0, 0, 0, 0, 1]
  stds = [0, 0, 0, 0, 2]
  sizes = [0, 0, 0, 0, 20]
  mean, size, std = list(InterpreterV2.compute_mean_values(means, sizes, stds))
  assert_equal(mean, 1.0)
  assert_equal(size, 20.0)
  assert_true(abs((std - 2.0)) < 0.001)

def test_classification_probabilities():
  distributions = [[0.1, 0.2, 0.7],
                   [0.1, 0.2, 0.7],
                   [0.1, 0.2, 0.7]]
  sizes = [1, 1, 1]
  res = list(InterpreterV2.compute_mean_distributions(distributions, sizes))
  assert_equal(res, [[0.1, 0.2, 0.7], 3])

  distributions = [[1.0, 0.0, 0.0],
                   [0.0, 1.0, 0.0],
                   [0.0, 0.0, 1.0]]
  sizes = [1, 1, 1]
  res = list(InterpreterV2.compute_mean_distributions(distributions, sizes))
  assert_equal(res, [[1/3., 1/3., 1/3.], 3])
