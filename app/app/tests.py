from django.test import SimpleTestCase
from app import calc


class CalcTestCase(SimpleTestCase):

    def test_add_numbers(self):
        res = calc.add(3, 6)
        self.assertEqual(res, 9)

    def test_subtract_numbers(self):
        res = calc.subtract(10, 5)
        self.assertEqual(res, 5)
