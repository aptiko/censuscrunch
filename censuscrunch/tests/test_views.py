from django.test import TestCase

from model_mommy import mommy

from censuscrunch import models


class CarrierListViewTestCase(TestCase):
    def setUp(self):
        mommy.make(models.Carrier, dot_number=42, number_of_power_units=5)
        mommy.make(models.Carrier, dot_number=43, number_of_power_units=10)
        mommy.make(models.Carrier, dot_number=44, number_of_power_units=15)

    def test_view_all(self):
        r = self.client.get("/")
        self.assertContains(r, "3 records")

    def test_filter_by_min_number_of_power_units(self):
        r = self.client.get("/?min_number_of_power_units=11")
        self.assertContains(r, "1 records")

    def test_filter_by_max_number_of_power_units(self):
        r = self.client.get("/?max_number_of_power_units=11")
        self.assertContains(r, "2 records")
