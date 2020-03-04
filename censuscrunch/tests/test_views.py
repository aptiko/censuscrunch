from django.test import TestCase, override_settings

from bs4 import BeautifulSoup
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


class NullValuesTestCase(TestCase):
    """Make sure nulls are shown as empty, not as the word "None".
    """

    def setUp(self):
        mommy.make(
            models.Carrier,
            id=7,
            legal_name="Killer Carrier",
            mcs150_date=None,
            mcs150_mileage=None,
            mcs150_mileage_year=None,
            number_of_power_units=None,
            number_of_drivers=None,
        )

    def test_no_none_in_carrier_list(self):
        r = self.client.get("/?q=killer")
        self.assertNotContains(r, "None")

    def test_no_none_in_detail(self):
        r = self.client.get("/carriers/7/")
        self.assertNotContains(r, "None")


class TableSortTestCase(TestCase):
    def setUp(self):
        mommy.make(
            models.Carrier,
            id=1,
            legal_name="Alice",
            dba_name="Zalice",
            physical_state="CA",
            number_of_power_units=5,
            number_of_drivers=5,
        )
        mommy.make(
            models.Carrier,
            id=2,
            legal_name="Bob",
            dba_name="Zbob",
            physical_state="NY",
            number_of_power_units=6,
            number_of_drivers=4,
        )
        mommy.make(
            models.Carrier,
            id=3,
            legal_name="Charlie",
            dba_name="",
            physical_state="MA",
            number_of_power_units=7,
            number_of_drivers=3,
        )

    def _get_sort_order(self, sort_terms):
        response = self._make_request(sort_terms)
        result = self._get_ids_from_response(response)
        return result

    def _make_request(self, sort_terms):
        url = "/?min_number_of_power_units=1&max_number_of_power_units=10&"
        url += "&".join([f"sort={x}" for x in sort_terms])
        return self.client.get(url)

    def _get_ids_from_response(self, response):
        soup = BeautifulSoup(response.content, "lxml")
        table_rows = soup.find("table").find_all("tr")
        table_rows = table_rows[1:]  # Skip header
        return [self._get_id_from_table_row(row) for row in table_rows]

    def _get_id_from_table_row(self, row):
        detail_url = row.td.a["href"]
        result = int(detail_url.split("/")[2])
        return result

    def test_sort_by_name(self):
        self.assertEqual(self._get_sort_order(["name"]), [3, 1, 2])

    def test_sort_by_name_reverse(self):
        self.assertEqual(self._get_sort_order(["-name"]), [2, 1, 3])

    def test_sort_by_state(self):
        self.assertEqual(self._get_sort_order(["physical_state"]), [1, 3, 2])

    def test_sort_by_state_reverse(self):
        self.assertEqual(self._get_sort_order(["-physical_state"]), [2, 3, 1])

    def test_sort_by_number_of_power_units(self):
        self.assertEqual(self._get_sort_order(["number_of_power_units"]), [1, 2, 3])

    def test_sort_by_number_of_power_units_reverse(self):
        self.assertEqual(self._get_sort_order(["-number_of_power_units"]), [3, 2, 1])

    def test_sort_by_number_of_drivers(self):
        self.assertEqual(self._get_sort_order(["number_of_drivers"]), [3, 2, 1])

    def test_sort_by_number_of_drivers_reverse(self):
        self.assertEqual(self._get_sort_order(["-number_of_drivers"]), [1, 2, 3])

    def test_sort_with_multiple_criteria(self):
        mommy.make(
            models.Carrier,
            id=4,
            legal_name="David",
            dba_name="",
            physical_state="MA",
            number_of_power_units=6,
            number_of_drivers=4,
        )
        self.assertEqual(
            self._get_sort_order(["number_of_power_units", "name"]), [1, 4, 2, 3]
        )
