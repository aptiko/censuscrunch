from django.test import TestCase, override_settings

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


@override_settings(CENSUSCRUNCH_ROW_LIMIT=2)
class CarrierListRowLimitTestCase(TestCase):
    def setUp(self):
        mommy.make(models.Carrier, dot_number=42, number_of_power_units=5)
        mommy.make(models.Carrier, dot_number=43, number_of_power_units=10)
        mommy.make(models.Carrier, dot_number=44, number_of_power_units=15)

    def test_row_limit_message(self):
        r = self.client.get("/")
        msg = "This search returns 3 rows. Change it so that it returns at most 2 rows."
        self.assertContains(r, msg, html=True)

    def test_no_results_if_above_row_limit(self):
        r = self.client.get("/")
        self.assertNotContains(r, "DOT number")
