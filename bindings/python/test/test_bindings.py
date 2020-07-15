#!/usr/bin/env python3

from test_utils import GTNModuleTestCase

import ctypes
import numpy as np
import struct

try:
    import gtn
except ImportError:
    print("Could not import gtn package - will skip tests")


class GraphTestCase(GTNModuleTestCase):
    def setUp(self):
        g = gtn.Graph(False)
        g.add_node(True)
        g.add_node()
        g.add_node()
        g.add_node()
        g.add_node(False, True)

        g.add_arc(0, 1, 0)
        g.add_arc(0, 2, 1)
        g.add_arc(1, 2, 0)
        g.add_arc(1, 1, 1, 1, 2.1)
        g.add_arc(2, 3, 2)
        self.g = g

    def test_graph_basic(self):
        self.assertEqual(self.g.num_nodes(), 5)
        self.assertEqual(self.g.num_start(), 1)
        self.assertEqual(self.g.num_accept(), 1)

        self.assertEqual(self.g.num_arcs(), 5)

    def test_graph_weights_get(self):
        weights = self.g.weights()
        weights_list = self.g.weights_to_list()
        weights_numpy = self.g.weights_to_numpy()
        expected = [0, 0, 0, 2.1, 0]
        # get weights as ptr
        length = 5
        get_weights_numpy = np.frombuffer(
            (ctypes.c_float * length).from_address(weights), np.float32
        )
        self.assertListAlmostEqual(get_weights_numpy.tolist(), expected, places=4)

        # get weights as list
        self.assertListAlmostEqual(weights_list, expected, places=4)

        # get weights as numpy
        self.assertListAlmostEqual(weights_numpy.tolist(), expected, places=4)

    def test_graph_weights_set(self):
        weights_original = self.g.weights()
        weights_new_expected = [1.1, -3.4, 0, 0.5, 0]

        # set weights as list
        self.g.set_weights(weights_new_expected)
        weights_new = self.g.weights_to_list()
        self.assertListAlmostEqual(weights_new, weights_new_expected, places=4)
        self.g.set_weights(weights_original)

        # set weights via numpy
        weights_new_arr = np.array(weights_new_expected, dtype="f")
        self.g.set_weights(weights_new_arr)
        weights_new = self.g.weights_to_numpy()
        self.assertListAlmostEqual(
            weights_new.tolist(), weights_new_arr.tolist(), places=4
        )
        self.g.set_weights(weights_original)

        # set weights via ptr
        weights_new_arr_ptr = weights_new_arr.__array_interface__["data"][0]
        self.g.set_weights(weights_new_arr_ptr)
        weights_new = self.g.weights_to_list()
        self.assertListAlmostEqual(weights_new, weights_new_arr.tolist(), places=4)
        self.g.set_weights(weights_original)


class FunctionsTestCase(GTNModuleTestCase):
    def test_scalar_ops(self):
        g1 = gtn.Graph()
        g1.add_node(True)
        g1.add_node(False, True)
        g1.add_arc(0, 1, 0, 0, 1.0)

        # Test negate:
        res = gtn.negate(g1)
        self.assertEqual(res.item(), -1.0)
        gtn.backward(res)
        self.assertEqual(g1.grad().item(), -1.0)
        g1.zero_grad()

        g2 = gtn.Graph()
        g2.add_node(True)
        g2.add_node(False, True)
        g2.add_arc(0, 1, 0, 0, 3.0)

        # Test add:
        res = gtn.add(g1, g2)
        self.assertEqual(res.item(), 4.0)
        gtn.backward(res)
        self.assertEqual(g1.grad().item(), 1.0)
        self.assertEqual(g2.grad().item(), 1.0)
        g1.zero_grad()
        g2.zero_grad()

        # Test subtract:
        res = gtn.subtract(g1, g2)
        self.assertEqual(res.item(), -2.0)
        gtn.backward(res)
        self.assertEqual(g1.grad().item(), 1.0)
        self.assertEqual(g2.grad().item(), -1.0)
