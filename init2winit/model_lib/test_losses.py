# coding=utf-8
# Copyright 2021 The init2winit Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for losses.py.

"""
import types

from absl.testing import absltest
from absl.testing import parameterized
from init2winit.model_lib import losses
import numpy as np


CLASSIFICATION_LOSSES = ['cross_entropy']
RECONSTRUCTION_LOSSES = [
    'sigmoid_binary_cross_entropy',
    'sigmoid_mean_squared_error',
]

CLASSIFICATION_TEST_DATA = [{
    'logits':
        np.array([[5, 3, 4, -3, 7], [2, 5, -5, 5, 6], [-6, -5, 8, -6, 4],
                  [15, 8, -6, 4, 2], [-7, 5, -6, 9, 0]]),
    'one_hot_targets':
        np.array([[1, 0, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 1], [0, 1, 0, 0, 0]]),
    'weights':
        None,
    'cross_entropy':
        8.956906,
}, {
    'logits':
        np.array([[4, 2, 0, -4, 5], [14, 2, -5, 10, 12], [20, -3, 7, -9, 6],
                  [5, 7, -1, 2, -8], [4, -7, 9, 0, 2]]),
    'one_hot_targets':
        np.array([[0, 1, 0, 0, 0], [0, 0, 0, 1, 0], [1, 0, 0, 0, 0],
                  [0, 0, 0, 0, 1], [0, 0, 1, 0, 0]]),
    'weights':
        np.array([2, 7, 0, 3, 0]),
    'cross_entropy':
        6.7589717,
}]

RECONSTRUCTION_TEST_DATA = [{
    'logits':
        np.array([[4, -5, 8, -10], [-5, 7, 4, 11], [12, 5, 5, -9],
                  [7, -11, -4, 8]]).astype(float),
    'targets':
        np.array([[0.05, 0.02, 0.96, 0.02], [0.05, 0.001, 0.5, 0.4],
                  [0.68, 0.92, 0.12, 0.22], [0.34, 0.44, 0.29, 0.2]]),
    'weights':
        None,
    'sigmoid_binary_cross_entropy':
        11.996754,
    'sigmoid_mean_squared_error':
        1.180348,
}, {
    'logits':
        np.array([[[4, -5], [8, -10]], [[-5, 7], [4, 11]], [[12, 5], [5, -9]],
                  [[7, -11], [-4, 8]]]).astype(float),
    'targets':
        np.array([[[0.05, 0.02], [0.96, 0.02]], [[0.05, 0.001], [0.5, 0.4]],
                  [[0.68, 0.92], [0.12, 0.22]], [[0.34, 0.44], [0.29, 0.2]]]),
    'weights':
        None,
    'sigmoid_binary_cross_entropy':
        11.996754,
    'sigmoid_mean_squared_error':
        1.180348,
}, {
    'logits':
        np.array([[4, -5, 8, -10], [-5, 7, 4, 11], [12, 5, 5, -9],
                  [7, -11, -4, 8]]).astype(float),
    'targets':
        np.array([[0.05, 0.02, 0.96, 0.02], [0.05, 0.001, 0.5, 0.4],
                  [0.68, 0.92, 0.12, 0.22], [0.34, 0.44, 0.29, 0.2]]),
    'weights':
        np.array([0, 4, 0, 2]),
    'sigmoid_binary_cross_entropy':
        16.259,
    'sigmoid_mean_squared_error':
        1.5073959,
}]

CROSS_ENTROPY_TEST_DATA = [{
    'logits':
        np.array([[4, 7], [-2, 5], [8, 6], [-10, -4], [3, -5]]).astype(float),
    'targets':
        np.array([[1, 0], [0, 1], [1, 0], [1, 0], [0, 1]]),
    'weights':
        None,
}, {
    'logits':
        np.array([[4, 7], [-2, 5], [8, 6], [-10, -4], [3, -5]]).astype(float),
    'targets':
        np.array([[1, 0], [0, 1], [1, 0], [1, 0], [0, 1]]),
    'weights':
        np.array([2, 0, 0, 6, 1]),
}]

CLASSIFICATION_KEYS = [
    (loss_name, loss_name) for loss_name in CLASSIFICATION_LOSSES
]
RECONSTRUCTION_KEYS = [
    (loss_name, loss_name) for loss_name in RECONSTRUCTION_LOSSES
]


class LossesTest(parameterized.TestCase):
  """Tests for losses.py."""

  def test_loss_fn_registry(self):
    for loss_name in losses._ALL_LOSS_FUNCTIONS:  # pylint: disable=protected-access
      loss_fn = losses.get_loss_fn(loss_name)
      self.assertIsInstance(loss_fn, types.FunctionType)
    with self.assertRaises(ValueError):
      losses.get_loss_fn('__test__loss__name__')

  def test_output_activation_fn_registry(self):
    activation_fn = losses.get_output_activation_fn(
        'cross_entropy')
    self.assertEqual(activation_fn.__name__, 'softmax')
    with self.assertRaises(ValueError):
      losses.get_output_activation_fn('__test__loss__name__')

  @parameterized.named_parameters(*CLASSIFICATION_KEYS)
  def test_classification_losses(self, loss_name):
    loss_fn = losses.get_loss_fn(loss_name)
    for data in CLASSIFICATION_TEST_DATA:
      self.assertAlmostEqual(
          loss_fn(data['logits'], data['one_hot_targets'], data['weights']),
          data[loss_name])

  @parameterized.named_parameters(*RECONSTRUCTION_KEYS)
  def test_regression_losses(self, loss_name):
    loss_fn = losses.get_loss_fn(loss_name)
    for data in RECONSTRUCTION_TEST_DATA:
      self.assertAlmostEqual(
          loss_fn(data['logits'], data['targets'], data['weights']),
          data[loss_name])

  def test_cross_entropy_loss_fn(self):
    for data in CROSS_ENTROPY_TEST_DATA:
      sigmoid_binary_ce_fn = losses.get_loss_fn('sigmoid_binary_cross_entropy')
      ce_fn = losses.get_loss_fn('cross_entropy')
      self.assertAlmostEqual(
          sigmoid_binary_ce_fn(
              np.array([logits[0] - logits[1] for logits in data['logits']]),
              np.array([targets[0] for targets in data['targets']]),
              data['weights']),
          ce_fn(data['logits'], data['targets'], data['weights']),
          places=5)


if __name__ == '__main__':
  absltest.main()
