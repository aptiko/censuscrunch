from django.db import models

CARRIER_OPERATION_CHOICES = (
    ("A", "Interstate"),
    ("B", "Intrastate Hazmat"),
    ("C", "Intrastate Non-Hazmat"),
)

STATES = (
    ("AK", "Alaska"),
    ("AL", "Alabama"),
    ("AR", "Arkansas"),
    ("AS", "American Samoa"),
    ("AZ", "Arizona"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DC", "District of Columbia"),
    ("DE", "Delaware"),
    ("FL", "Florida"),
    ("GA", "Georgia"),
    ("GU", "Guam"),
    ("HI", "Hawaii"),
    ("IA", "Iowa"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("MA", "Massachusetts"),
    ("MD", "Maryland"),
    ("ME", "Maine"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MO", "Missouri"),
    ("MP", "Northern Mariana Islands"),
    ("MS", "Mississippi"),
    ("MT", "Montana"),
    ("NA", "National"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("NE", "Nebraska"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NV", "Nevada"),
    ("NY", "New York"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PA", "Pennsylvania"),
    ("PR", "Puerto Rico"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VA", "Virginia"),
    ("VI", "Virgin Islands"),
    ("VT", "Vermont"),
    ("WA", "Washington"),
    ("WI", "Wisconsin"),
    ("WV", "West Virginia"),
    ("WY", "Wyoming"),
)


class Carrier(models.Model):
    dot_number = models.PositiveIntegerField(unique=True)
    legal_name = models.CharField(max_length=150)
    dba_name = models.CharField(max_length=150, blank=True)
    carrier_operation = models.CharField(
        max_length=1, choices=CARRIER_OPERATION_CHOICES
    )
    hm = models.BooleanField()
    pc = models.BooleanField()
    physical_address = models.CharField(max_length=100)
    physical_city = models.CharField(max_length=30)
    physical_state = models.CharField(max_length=2, choices=STATES)
    physical_zip = models.CharField(max_length=10)
    physical_country = models.CharField(max_length=2, choices=[("US", "United States")])
    mailing_address = models.CharField(max_length=100)
    mailing_city = models.CharField(max_length=30)
    mailing_state = models.CharField(max_length=2, choices=STATES)
    mailing_zip = models.CharField(max_length=10)
    mailing_country = models.CharField(max_length=2, choices=[("US", "United States")])
    tel = models.CharField(max_length=14)
    fax = models.CharField(max_length=14, blank=True)
    email = models.EmailField()
    mcs150_date = models.DateField(null=True, blank=True)
    mcs150_mileage = models.BigIntegerField(null=True, blank=True)
    mcs150_mileage_year = models.PositiveSmallIntegerField(null=True, blank=True)
    date_added_mcmis = models.DateField()
    oic_state = models.CharField(max_length=2, choices=STATES)
    number_of_power_units = models.PositiveIntegerField(null=True, blank=True)
    number_of_drivers = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["physical_state", "physical_zip", "physical_address"]),
            models.Index(fields=["mailing_state", "mailing_zip", "mailing_address"]),
            models.Index(fields=["mcs150_date"]),
            models.Index(fields=["date_added_mcmis"]),
            models.Index(fields=["oic_state"]),
            models.Index(fields=["number_of_power_units"]),
            models.Index(fields=["number_of_drivers"]),
        ]
        ordering = ("dot_number",)

    def __str__(self):
        return f"{self.legal_name} ({self.dot_number})"
