import datetime as dt
from io import StringIO

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
            physical_state="NY",
        )
        mommy.make(
            models.Carrier,
            id=2,
            dot_number=43,
            number_of_power_units=10,
            legal_name="Transport Greatness",
            dba_name="",
            physical_state="CA",
        )
        mommy.make(
            models.Carrier,
            id=3,
            dot_number=44,
            number_of_power_units=15,
            legal_name="Jociel",
            dba_name="Johnson Logistics",
            physical_state="MA",
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

    def test_filter_by_state(self):
        r = self.client.get("/?state=ca")
        self.assertContains(r, "1 records")
        self.assertContains(r, "Transport Greatness")

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


class CarrierListCsvTestCase(TestCase):
    def setUp(self):
        mommy.make(
            models.Carrier,
            dot_number=42,
            legal_name="Killer Carrier, Inc",
            dba_name="Killer Carrier",
            carrier_operation="C",
            hm=False,
            pc=True,
            physical_address="0 Abyss Alley",
            physical_city="Nowhere",
            physical_state="NY",
            physical_zip="12345",
            physical_country="US",
            mailing_address="0 Abyss Alley",
            mailing_city="Nowhere",
            mailing_state="NY",
            mailing_zip="12345",
            mailing_country="US",
            tel="+123456789",
            fax="+198765432",
            email="alicebrown@killercarrier.com",
            mcs150_date=dt.date(2020, 3, 5),
            mcs150_mileage=18725329,
            mcs150_mileage_year=2020,
            date_added_mcmis=dt.date(2019, 2, 4),
            oic_state="MA",
            number_of_power_units=5,
            number_of_drivers=4,
        )
        mommy.make(
            models.Carrier,
            dot_number=43,
            legal_name="Transport Greatness",
            dba_name="",
            carrier_operation="",
            hm=True,
            pc=False,
            physical_address="",
            physical_city="",
            physical_state="",
            physical_zip="",
            physical_country="",
            mailing_address="",
            mailing_city="",
            mailing_state="",
            mailing_zip="",
            mailing_country="",
            tel="",
            fax="",
            email="",
            mcs150_date=None,
            mcs150_mileage=None,
            mcs150_mileage_year=None,
            date_added_mcmis=dt.date(2019, 1, 3),
            oic_state="",
            number_of_power_units=None,
            number_of_drivers=None,
        )

    def test_csv(self):
        r = self.client.get("/?q=r&format=csv")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "text/csv")
        result = StringIO(r.content.decode())
        header, first_line, second_line = result.readlines()
        self.assertEqual(
            header,
            '"DOT_NUMBER","LEGAL_NAME","DBA_NAME","CARRIER_OPERATION","HM_FLAG",'
            '"PC_FLAG","PHY_STREET","PHY_CITY","PHY_STATE","PHY_ZIP","PHY_COUNTRY",'
            '"MAILING_STREET","MAILING_CITY","MAILING_STATE","MAILING_ZIP",'
            '"MAILING_COUNTRY","TELEPHONE","FAX","EMAIL_ADDRESS","MCS150_DATE",'
            '"MCS150_MILEAGE","MCS150_MILEAGE_YEAR","ADD_DATE","OIC_STATE",'
            '"NBR_POWER_UNIT","DRIVER_TOTAL"\r\n',
        )
        self.assertEqual(
            first_line,
            '42,"Killer Carrier, Inc","Killer Carrier","C","N","Y",'
            '"0 Abyss Alley","Nowhere","NY","12345","US","0 Abyss Alley",'
            '"Nowhere","NY","12345","US","+123456789",'
            '"+198765432","alicebrown@killercarrier.com","05-MAR-20",18725329,2020,'
            '"04-FEB-19","MA",5,4\r\n',
        )
        self.assertEqual(
            second_line,
            '43,"Transport Greatness","","","Y","N",'
            '"","","","","","",'
            '"","","","","",'
            '"","","","","",'
            '"03-JAN-19","","",""\r\n',
        )


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

    def test_no_csv_results_if_above_row_limit(self):
        r = self.client.get("/?max_number_of_power_units=15&format=csv")
        self.assertEqual(r.status_code, 400)


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
