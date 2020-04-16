import unittest
from typing import Optional

from hypothesis import given

from electionguard.group import (
    P,
    Q,
    ElementModP,
    ElementModQ,
    mult_inv_p,
    ONE_MOD_P,
    mult_p,
    ZERO_MOD_P,
    G,
    ONE_MOD_Q,
    g_pow_p,
    ZERO_MOD_Q,
    R,
    G_INV,
    int_to_p,
    int_to_q,
    add_q,
    int_to_p_unchecked,
    int_to_q_unchecked,
    unwrap_optional,
    match_optional,
    get_or_else_optional,
    flatmap_optional,
)
from electionguardtest.group import (
    arb_element_mod_p_no_zero,
    arb_element_mod_p,
    arb_element_mod_q,
    arb_element_mod_q_no_zero,
)


class TestModularArithmetic(unittest.TestCase):
    def test_no_mult_inv_of_zero(self):
        self.assertRaises(Exception, mult_inv_p, ZERO_MOD_P)

    @given(arb_element_mod_p_no_zero())
    def test_mult_inverses(self, elem: ElementModP):
        inv = mult_inv_p(elem)
        self.assertEqual(mult_p(elem, inv), ONE_MOD_P)

    @given(arb_element_mod_p())
    def test_mult_identity(self, elem: ElementModP):
        self.assertEqual(elem, mult_p(elem))

    def test_mult_noargs(self):
        self.assertEqual(ONE_MOD_P, mult_p())

    def test_add_noargs(self):
        self.assertEqual(ZERO_MOD_Q, add_q())

    def test_properties_for_constants(self):
        self.assertNotEqual(G, 1)
        self.assertEqual((R * Q) % P, P - 1)
        self.assertLess(Q, P)
        self.assertLess(G, P)
        self.assertLess(G_INV, P)
        self.assertLess(R, P)

    def test_simple_powers(self):
        gp = int_to_p(G)
        self.assertEqual(gp, g_pow_p(ONE_MOD_Q))
        self.assertEqual(ONE_MOD_P, g_pow_p(ZERO_MOD_Q))

    @given(arb_element_mod_q())
    def test_in_bounds_q(self, q: ElementModQ):
        self.assertTrue(q.is_in_bounds())
        too_big = q.to_int() + Q
        too_small = q.to_int() - Q
        self.assertFalse(int_to_q_unchecked(too_big).is_in_bounds())
        self.assertFalse(int_to_q_unchecked(too_small).is_in_bounds())
        self.assertEqual(None, int_to_q(too_big))
        self.assertEqual(None, int_to_q(too_small))

    @given(arb_element_mod_p())
    def test_in_bounds_p(self, p: ElementModP):
        self.assertTrue(p.is_in_bounds())
        too_big = p.to_int() + P
        too_small = p.to_int() - P
        self.assertFalse(int_to_p_unchecked(too_big).is_in_bounds())
        self.assertFalse(int_to_p_unchecked(too_small).is_in_bounds())
        self.assertEqual(None, int_to_p(too_big))
        self.assertEqual(None, int_to_p(too_small))

    @given(arb_element_mod_q_no_zero())
    def test_in_bounds_q_no_zero(self, q: ElementModQ):
        self.assertTrue(q.is_in_bounds_no_zero())
        self.assertFalse(ZERO_MOD_Q.is_in_bounds_no_zero())
        self.assertFalse(int_to_q_unchecked(q.to_int() + Q).is_in_bounds_no_zero())
        self.assertFalse(int_to_q_unchecked(q.to_int() - Q).is_in_bounds_no_zero())

    @given(arb_element_mod_p_no_zero())
    def test_in_bounds_p_no_zero(self, p: ElementModP):
        self.assertTrue(p.is_in_bounds_no_zero())
        self.assertFalse(ZERO_MOD_P.is_in_bounds_no_zero())
        self.assertFalse(int_to_p_unchecked(p.to_int() + P).is_in_bounds_no_zero())
        self.assertFalse(int_to_p_unchecked(p.to_int() - P).is_in_bounds_no_zero())


class TestOptionalFunctions(unittest.TestCase):
    def test_unwrap(self):
        good: Optional[int] = 3
        bad: Optional[int] = None

        self.assertEqual(unwrap_optional(good), 3)
        self.assertRaises(Exception, unwrap_optional, bad)

    def test_match(self):
        good: Optional[int] = 3
        bad: Optional[int] = None

        self.assertEqual(5, match_optional(good, lambda: 1, lambda x: x + 2))
        self.assertEqual(1, match_optional(bad, lambda: 1, lambda x: x + 2))

    def test_get_or_else(self):
        good: Optional[int] = 3
        bad: Optional[int] = None

        self.assertEqual(3, get_or_else_optional(good, 5))
        self.assertEqual(5, get_or_else_optional(bad, 5))

    def test_flatmap(self):
        good: Optional[int] = 3
        bad: Optional[int] = None

        self.assertEqual(5, unwrap_optional(flatmap_optional(good, lambda x: x + 2)))
        self.assertIsNone(flatmap_optional(bad, lambda x: x + 2))
