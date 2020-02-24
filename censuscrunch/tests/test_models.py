from django.test import TestCase

from model_mommy import mommy

from censuscrunch import models


class CarrierTestCase(TestCase):
    def test_create(self):
        carrier = models.Carrier(
            dot_number=42,
            legal_name="Killer Carrier",
            dba_name="Killer Carrier",
            carrier_operation="A",
            hm=True,
            pc=True,
            physical_address="12345 6th Street",
            physical_city="New York",
            physical_state="NY",
            physical_zip="54321",
            physical_country="US",
            mailing_address="12345 6th Street",
            mailing_city="New York",
            mailing_state="NY",
            mailing_zip="54321",
            mailing_country="US",
            tel="12345678",
            email="john@killercarrier.com",
            date_added_mcmis="2020-02-24",
            oic_state="NY",
            number_of_power_units=42,
            number_of_drivers=84,
        )
        carrier.save()
        self.assertEqual(models.Carrier.objects.first().dba_name, "Killer Carrier")

    def test_update(self):
        mommy.make(models.Carrier)
        carrier = models.Carrier.objects.first()
        carrier.dba_name = "Killer Carrier"
        carrier.save()
        self.assertEqual(models.Carrier.objects.first().dba_name, "Killer Carrier")

    def test_delete(self):
        mommy.make(models.Carrier)
        carrier = models.Carrier.objects.first()
        carrier.delete()
        self.assertEqual(models.Carrier.objects.count(), 0)

    def test_str(self):
        carrier = mommy.make(models.Carrier, dot_number=42, legal_name="Killer Carrier")
        self.assertEqual(str(carrier), "Killer Carrier (42)")
