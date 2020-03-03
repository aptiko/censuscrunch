from django.test import TestCase, override_settings

from model_mommy import mommy

from censuscrunch import models


class CarrierListViewTestCase(TestCase):
    def setUp(self):
        mommy.make(
            models.Carrier,
            id=1,
            dot_number=42,
            number_of_power_units=5,
            legal_name="Killer Carrier, Inc",
            dba_name="Killer Carrier",
        )
        mommy.make(
            models.Carrier,
            id=2,
            dot_number=43,
            number_of_power_units=10,
            legal_name="Transport Greatness",
            dba_name="",
        )
        mommy.make(
            models.Carrier,
            id=3,
            dot_number=44,
            number_of_power_units=15,
            legal_name="Jociel",
            dba_name="Johnson Logistics",
        )

    def test_no_queries_when_no_query(self):
        with self.assertNumQueries(0):
            self.client.get("/")

    def test_message_when_no_query(self):
        r = self.client.get("/")
        self.assertNotContains(r, "0 records")

    def test_filter_by_min_number_of_power_units(self):
        r = self.client.get("/?min_number_of_power_units=11")
        self.assertContains(r, "1 records")

    def test_filter_by_max_number_of_power_units(self):
        r = self.client.get("/?max_number_of_power_units=11")
        self.assertContains(r, "2 records")

    def test_link_to_detail(self):
        r = self.client.get("/?max_number_of_power_units=11")
        self.assertContains(r, '<a href="/carriers/2/">')

    def test_simple_search1(self):
        r = self.client.get("/?q=killer")
        self.assertContains(r, "1 records")
        self.assertContains(r, "Killer Carrier")

    def test_simple_search2(self):
        r = self.client.get("/?q=great")
        self.assertContains(r, "1 records")
        self.assertContains(r, "Transport Greatness")

    def test_simple_search3(self):
        r = self.client.get("/?q=a")
        self.assertContains(r, "2 records")
        self.assertContains(r, "Killer Carrier")
        self.assertContains(r, "Transport Greatness")


@override_settings(CENSUSCRUNCH_ROW_LIMIT=2)
class CarrierListRowLimitTestCase(TestCase):
    def setUp(self):
        mommy.make(models.Carrier, dot_number=42, number_of_power_units=5)
        mommy.make(models.Carrier, dot_number=43, number_of_power_units=10)
        mommy.make(models.Carrier, dot_number=44, number_of_power_units=15)

    def test_row_limit_message(self):
        r = self.client.get("/?max_number_of_power_units=15")
        msg = "This search returns 3 rows. Change it so that it returns at most 2 rows."
        self.assertContains(r, msg, html=True)

    def test_no_results_if_above_row_limit(self):
        r = self.client.get("/?max_number_of_power_units=15")
        self.assertNotContains(r, "Name")


class CarrierDetailTestCase(TestCase):
    def setUp(self):
        mommy.make(
            models.Carrier,
            id=7,
            dot_number=42,
            legal_name="Super Duper Carriers",
            carrier_operation="C",
        )

    def test_legal_name(self):
        r = self.client.get("/carriers/7/")
        self.assertContains(r, "Super Duper Carriers")

    def test_carrier_operation(self):
        r = self.client.get("/carriers/7/")
        self.assertContains(r, "C (Intrastate Non-Hazmat)", html=True)
