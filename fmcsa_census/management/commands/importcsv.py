import csv
import datetime as dt
from collections import OrderedDict, namedtuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.utils import DataError, IntegrityError

from fmcsa_census.models import Carrier

CarrierAttribute = namedtuple("CarrierAttribute", ["name", "conversion_function"])


def str2bool(s):
    if s not in ("Y", "N"):
        raise ValueError(f"'{s} is not one of 'Y' and 'N'")
    return s == "Y"


def str2date(s):
    if s:
        return dt.datetime.strptime(s, "%d-%b-%y").date()
    else:
        return None


def str2int(s):
    if s:
        return int(s)
    else:
        return None


CARRIER_ATTRIBUTES = OrderedDict(
    (
        ("DOT_NUMBER", CarrierAttribute("dot_number", str)),
        ("LEGAL_NAME", CarrierAttribute("legal_name", str)),
        ("DBA_NAME", CarrierAttribute("dba_name", str)),
        ("CARRIER_OPERATION", CarrierAttribute("carrier_operation", str)),
        ("HM_FLAG", CarrierAttribute("hm", str2bool)),
        ("PC_FLAG", CarrierAttribute("pc", str2bool)),
        ("PHY_STREET", CarrierAttribute("physical_address", str)),
        ("PHY_CITY", CarrierAttribute("physical_city", str)),
        ("PHY_STATE", CarrierAttribute("physical_state", str)),
        ("PHY_ZIP", CarrierAttribute("physical_zip", str)),
        ("PHY_COUNTRY", CarrierAttribute("physical_country", str)),
        ("MAILING_STREET", CarrierAttribute("mailing_address", str)),
        ("MAILING_CITY", CarrierAttribute("mailing_city", str)),
        ("MAILING_STATE", CarrierAttribute("mailing_state", str)),
        ("MAILING_ZIP", CarrierAttribute("mailing_zip", str)),
        ("MAILING_COUNTRY", CarrierAttribute("mailing_country", str)),
        ("TELEPHONE", CarrierAttribute("tel", str)),
        ("FAX", CarrierAttribute("fax", str)),
        ("EMAIL_ADDRESS", CarrierAttribute("email", str)),
        ("MCS150_DATE", CarrierAttribute("mcs150_date", str2date)),
        ("MCS150_MILEAGE", CarrierAttribute("mcs150_mileage", str2int)),
        ("MCS150_MILEAGE_YEAR", CarrierAttribute("mcs150_mileage_year", str2int)),
        ("ADD_DATE", CarrierAttribute("date_added_mcmis", str2date)),
        ("OIC_STATE", CarrierAttribute("oic_state", str)),
        ("NBR_POWER_UNIT", CarrierAttribute("number_of_power_units", str2int)),
        ("DRIVER_TOTAL", CarrierAttribute("number_of_drivers", str2int)),
    )
)


class Command(BaseCommand):
    help = "Discards database and imports FCMSA's CSV file"

    def add_arguments(self, parser):
        parser.add_argument("filename")

    def handle(self, *args, **options):
        self.filename = options["filename"]
        self.verbosity = options["verbosity"]
        self._delete_existing_records()
        self._import_csv()

    def _delete_existing_records(self):
        Carrier.objects.all().delete()

    def _import_csv(self):
        try:
            with open(self.filename) as f:
                csvreader = csv.reader(f)
                self._read_csv(csvreader)
        except OSError as e:
            raise CommandError(str(e))

    def _read_csv(self, csvreader):
        self._read_csv_heading(csvreader)
        self._read_csv_body(csvreader)

    def _read_csv_heading(self, csvreader):
        if next(csvreader) != list(CARRIER_ATTRIBUTES.keys()):
            raise CommandError("The file does not have the expected heading.")

    def _read_csv_body(self, csvreader):
        transaction.set_autocommit(False)
        for i, row in enumerate(csvreader, start=2):
            try:
                self._create_carrier(row)
            except (ValueError, IntegrityError, DataError) as e:
                raise CommandError(f"Error in line {i}: {str(e)}")
            self._show_progress(i)
            if ((i // 10_000) * 10_000) == i:
                transaction.commit()
        transaction.commit()

    def _show_progress(self, i):
        if self.verbosity >= 1 and ((i // 10_000) * 10_000 == i):
            self.stderr.write(f"\r{i:,} records completed")

    def _create_carrier(self, row):
        azip = zip(CARRIER_ATTRIBUTES.values(), row)
        kwargs = {attr.name: attr.conversion_function(value) for attr, value in azip}
        Carrier.objects.create(**kwargs)
