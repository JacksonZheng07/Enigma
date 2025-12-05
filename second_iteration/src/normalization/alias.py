"""
some of the alias
"""
from typing import Dict
import re


def standardize_alias_key(col: str) -> str:
    """
    Standardize alias keys into snake_case so we can match provider fields.
    """
    col = (
        col.strip()
        .replace("-", " ")
        .replace(".", " ")
        .replace("/", " ")
        .replace(",", " ")
        .replace("?", " ")
        .replace("!", " ")
        .replace("@", " ")
        .replace("%", " ")
        .replace("&", " ")
    )
    col = re.sub(r"\s+", " ", col)
    col = col.replace(" ", "_").lower()
    col = re.sub(r"_+", "_", col)
    return col.rstrip("_")


def _normalize_aliases(source: Dict[str, str]) -> Dict[str, str]:
    normalized: Dict[str, str] = {}
    for alias, canonical in source.items():
        normalized[standardize_alias_key(alias)] = canonical
    return normalized


RAW_ALIASES: Dict[str, str] = {
    # BUSINESS NAME / DBA / ENTITY NAME
    "Business Name": "business_name",
    "Bus Name": "business_name",
    "Entity Name": "business_name",
    "Company Name": "business_name",
    "Corp Name": "business_name",
    "Corporate Name": "business_name",
    "Legal Business Name": "business_name",
    "Registered Name": "business_name",
    "Registered Business Name": "business_name",
    "Official Name": "business_name",
    "Legal Name": "business_name",
    "Name": "business_name",
    "Org Name": "business_name",
    "Organization Name": "business_name",
    "Firm Name": "business_name",
    "Store Name": "business_name",
    "Outlet Name": "business_name",
    "business_name": "business_name",

    # DBA / Trade Name / Fictitious Name
    "DBA": "dba",
    "D/B/A": "dba",
    "Doing Business As": "dba",
    "Trade Name": "dba",
    "Trading Name": "dba",
    "Fictitious Name": "dba",
    "Assumed Name": "dba",
    "Business Alias": "dba",
    "Alternate Name": "dba",
    "Alias Name": "dba",
    "Alternate Business Name": "dba",
    "dba": 'dba',

     # PEOPLE (OWNERS, CONTACTS, OFFICERS)
     # Simple person fields
    "First Name": "first_name",
    "Firstname": "first_name",
    "Given Name": "first_name",
    "FName": "first_name",
    "First_Name": "first_name",
    "first_name": "first_name",

    "Middle Name": "middle_name",
    "Middle Initial": "middle_name",
    "middle_name": "middle_name",
    "M.I.": "middle_name",
    "MI": "middle_name",

    "Last Name": "last_name",
    "Lastname": "last_name",
    "Surname": "last_name",
    "Family Name": "last_name",
    "LName": "last_name",
    "Last_Name": "last_name",
    "last_name": 'last_name',

    "Full Name": "full_name",
    'full_name': 'full_name',
    "Contact Name": "contact_name",
    "Contact Person": "contact_name",
    "Primary Contact": "contact_name",
    "Contact": "contact_name",

    # Owner
    "Owner": "owner_name",
    "Owner Name": "owner_name",
    "Primary Owner": "owner_name",
    "Business Owner": "owner_name",
    "Registered Owner": "owner_name",
    'owner_name': 'owner_name',

    # Officers / agents
    "Officer Name": "officer_name",
    "Corporate Officer": "officer_name",
    "Chief Executive Officer": "officer_name",
    "CEO": "officer_name",
    "President": "officer_name",
    "Vice President": "officer_name",
    "Secretary": "officer_name",
    "Treasurer": "officer_name",
    "Director": "officer_name",
    "officer_name": 'officer_name',

    "Registered Agent": "registered_agent",
    "Agent Name": "registered_agent",
    "Service Agent": "registered_agent",
    "registered_agent": "registered_agent",

    "Authorized Representative": "authorized_representative",
    "Authorized Signatory": "authorized_representative",
    "authorized_representative": "authorized_representative",

    # LICENSE / PERMIT / REGISTRATION FIELDS
    "License Number": "license_number",
    "License #": "license_number",
    "Lic Number": "license_number",
    "Lic #": "license_number",
    "License No": "license_number",
    "License_ID": "license_number",
    "License Id": "license_number",
    "DCA License Number": "license_number",
    "Permit Number": "license_number",
    "Permit #": "license_number",
    "Permit Id": "license_number",
    "Registration Number": "license_number",
    "Registration #": "license_number",
    "Registration Id": "license_number",
    "Certificate Number": "license_number",
    "Certificate #": "license_number",
    "Certification Number": "license_number",
    "license_number": "license_number",

    "License Type": "license_type",
    "Lic Type": "license_type",
    "Permit Type": "license_type",
    "Registration Type": "license_type",
    "License Class": "license_type",
    "License Category": "license_type",
    "Permit Class": "license_type",
    "Permit Category": "license_type",
    "license_type": "license_type",

    "License Status": "license_status",
    "Lic Status": "license_status",
    "Permit Status": "license_status",
    "Status": "license_status",
    "Current Status": "license_status",
    "Record Status": "license_status",
    "Application Status": "license_status",
    "license_status": "license_status",

    "Issue Date": "issue_date",
    "Issued Date": "issue_date",
    "License Issue Date": "issue_date",
    "Permit Issue Date": "issue_date",
    "Registration Issue Date": "issue_date",
    "issue_date": 'issue_date',

    "Expiration Date": "expiration_date",
    "Expiry Date": "expiration_date",
    "License Expiration Date": "expiration_date",
    "Permit Expiration Date": "expiration_date",
    "Registration Expiration Date": "expiration_date",
    "License Expiry": "expiration_date",
    "Permit Expiry": "expiration_date",
    "expiration_date": "expiration_date",

    "Renewal Date": "renewal_date",
    "Renewal Due Date": "renewal_date",
    "Renew By": "renewal_date",
    "renewal_date": "renewal_date",

    "Valid From": "valid_from",
    "valid_from": "valid_from",
    "Valid To": "valid_to",
    "Valid Until": "valid_to",
    "valid_to": "valid_to",
    "Effective Date": "effective_date",
    "effective_date": "effective_date",
    "Activation Date": "active_date",
    "active_date": "active_date",
    "Activated Date": "active_date",
    "Deactivation Date": "inactive_date",
    "inactive_date": "inactive_date",

    # IDENTIFIERS (EIN, BIN, TAX IDS, ETC.)
    "EIN": "ein",
    "FEIN": "ein",
    "Employer Identification Number": "ein",
    "Federal EIN": "ein",
    "Tax ID": "ein",
    "Tax Identification Number": "ein",
    "Federal Tax ID": "ein",
    "Federal Tax Identification Number": "ein",
    "IRS Number": "ein",
    "ein": "ein",

    "BIN": "bin",
    "Bank Identification Number": "bin",
    "bank identification number": "bin",
    "Bin": "bin",
    "bin": "bin",

    "CRS": "crs_id",
    "crs": "crs_id",
    "CRS Number": "crs_id",
    "crs_number": "crs_id",
    "crs_id": "crs_id",
    "State Tax ID": "state_tax_id",
    "state_tax_id": "state_tax_id",
    "State Tax Identification Number": "state_tax_id",

    "UBI": "ubi",
    "UBI Number": "ubi",
    "Unified Business Identifier": "ubi",
    "ubi": "ubi",

    "Entity ID": "entity_id",
    "Entity Number": "entity_id",
    "Entity_Id": "entity_id",
    "Business ID": "entity_id",
    "Business Identifier": "entity_id",
    "Registration ID": "entity_id",
    "Registration Identifier": "entity_id",
    "Org ID": "entity_id",
    "Organization ID": "entity_id",
    "registration_iD": "entity_id",
    "entity_id": "entity_id",

    "Record Number": "record_number",
    "Record #": "record_number",
    "record": "record_number",
    "Unique ID": "record_number",
    "Unique Identifier": "record_number",
    "record_number": "record_number",

    # IMPORTANT DATES
    "Created Date": "created_date",
    "Creation Date": "created_date",
    "Date Created": "created_date",
    "Record Created": "created_date",

    "File Date": "file_date",
    "Filing Date": "file_date",
    "Date Filed": "file_date",

    "Updated Date": "updated_date",
    "Modified Date": "updated_date",
    "Last Updated": "updated_date",
    "Last Modified": "updated_date",
    "Update Date": "updated_date",

    "Start Date": "start_date",
    "Start_Date": "start_date",
    "Opening Date": "start_date",
    "Opened Date": "start_date",

    "End Date": "end_date",
    "End_Date": "end_date",
    "Closing Date": "end_date",
    "Closed Date": "end_date",

    "Inactive Date": "inactive_date",
    "Closure Date": "inactive_date",
    "Dissolution Date": "inactive_date",
    "Termination Date": "inactive_date",

    # ADDRESS COMPONENTS
    # Building number
    "Building": "building_number",
    "Building Number": "building_number",
    "Bldg Number": "building_number",
    "House Number": "building_number",
    "Address Building": "building_number",
    "Premise Number": "building_number",
    "Street Number": "building_number",
    "St Number": "building_number",

    # Street name
    "Street": "street_name",
    "Street Name": "street_name",
    "Address Street Name": "street_name",
    "St Name": "street_name",
    "Road": "street_name",
    "Rd": "street_name",
    "Avenue": "street_name",
    "Ave": "street_name",
    "Boulevard": "street_name",
    "Blvd": "street_name",
    "Lane": "street_name",
    "Ln": "street_name",
    "Drive": "street_name",
    "Dr": "street_name",
    "Highway": "street_name",
    "Hwy": "street_name",

    # Full address
    "Address": "address",
    "Street Address": "address",
    "Address1": "address",
    "Address 1": "address",
    "Address Line 1": "address",
    "Addr1": "address",
    "Premise Address": "address",
    "Location": "address",
    "Business Address": "address",
    "Site Address": "address",
    "Property Address": "address",
    "Physical Address": "address",
    "Service Address": "address",

    # Address line 2
    "Address2": "address2",
    "Address 2": "address2",
    "Address Line 2": "address2",
    "Addr2": "address2",
    "Suite": "address2",
    "Apt": "address2",
    "Apartment": "address2",
    "Unit": "address2",
    "Floor": "address2",
    "Building Unit": "address2",

    # City / locality
    "City": "city",
    "Town": "city",
    "Municipality": "city",
    "Village": "city",
    "Locality": "city",
    "Address City": "city",

    # State / region
    "State": "state",
    "Address State": "state",
    "Province": "state",
    "Region": "state",
    "State/Province": "state",

    # County / borough / district
    "County": "county",
    "Parish": "county",
    "County Name": "county",
    "Borough": "borough",
    "Address Borough": "borough",
    "Boro": "borough",
    "District": "district",
    "District Name": "district",

    "location": 'location',
    'cord_pair': 'location',
    "cord": 'location',


    # ZIP / Postal Code (including your originals)
    "ZIP": "zip_code",
    "Zip": "zip_code",
    "Zip Code": "zip_code",
    "ZIP Code": "zip_code",
    "zip": "zip_code",
    "zipcode": "zip_code",
    "Postal Code": "zip_code",
    "PostalCode": "zip_code",
    "Postcode": "zip_code",
    "Post Code": "zip_code",
    "Mail ZIP": "zip_code",
    "Mail Zip": "zip_code",
    "Zip5": "zip_code",
    "Zip 5": "zip_code",
    "Zip+4": "zip4",
    "Zip 4": "zip4",
    "ZIP+4": "zip4",
    "Address ZIP": "zip_code",
    "address_zip": "zip_code",

    # Mailing address variants
    "Mailing Address": "mailing_address",
    "Mail Address": "mailing_address",
    "Mail Street": "mailing_address",
    "Mail City": "mail_city",
    "Mail State": "mail_state",
    "Mail ZIP Code": "mail_zip",

    # GEO COORDINATES
    "Latitude": "latitude",
    "latitude": "latitude",
    "Lat": "latitude",
    "LAT": "latitude",
    "lat": "latitude",
    "Y": "latitude",
    "Ycoord": "latitude",
    "Y Coordinate": "latitude",
    "Y Coordinate (Latitude)": "latitude",
    "Geo Latitude": "latitude",

    "Longitude": "longitude",
    "longitude": "longitude",
    "Long": "longitude",
    "Lon": "longitude",
    'lon': 'longitude',
    "lng": "longitude",
    "LNG": "longitude",
    "X": "longitude",
    "Xcoord": "longitude",
    "X Coordinate": "longitude",
    "X Coordinate (Longitude)": "longitude",
    "Geo Longitude": "longitude",

    # CONTACT INFO
    "Phone": "phone",
    "Phone Number": "phone",
    "Contact Number": "phone",
    "Business Phone": "phone",
    "Primary Phone": "phone",
    "Telephone": "phone",
    "Tel": "phone",
    "Contact Phone Number": "phone",
    "Daytime Phone": "phone",
    'phone': 'phone',

    "Fax": "fax",
    "Fax Number": "fax",
    'fax' : 'fax',

    "Email": "email",
    "E-mail": "email",
    "Email Address": "email",
    "Contact Email": "email",

    "Website": "website",
    "Web Site": "website",
    "URL": "website",
    "Web Address": "website",
    "Homepage": "website",

    # INDUSTRY / CATEGORY / CODES
    "Industry": "industry",
    "Business Category": "industry",
    "Category": "industry",
    "Business Type Description": "industry",
    "Description of Business": "industry",
    "Primary Business Activity": "industry",

    "NAICS": "naics",
    "NAICS Code": "naics",
    "Primary NAICS": "naics",
    "NAICS Description": "naics_description",

    "SIC": "sic",
    "SIC Code": "sic",
    "Primary SIC": "sic",
    "SIC Description": "sic_description",

    "Business Type": "business_type",
    "Entity Type": "entity_type",
    "Ownership Type": "ownership_type",

    # DESCRIPTION / NOTES
    "Description": "description",
    "Business Description": "description",
    "Activity Description": "description",
    "Notes": "notes",
    "Remarks": "notes",
    "Comments": "notes",
    "Comment": "notes",
    "Additional Info": "notes",

    # NUMERIC / SIZE FIELDS
    "Employees": "num_employees",
    "Employee Count": "num_employees",
    "Number of Employees": "num_employees",
    "Employees (Total)": "num_employees",
    "Full-time Employees": "num_employees_fulltime",
    "Part-time Employees": "num_employees_parttime",

    "Revenue": "revenue",
    "Annual Revenue": "revenue",
    "annual_revenue": 'revenue',
    "Sales": "revenue",
    "Sales Volume": "revenue",
    "sales_volumne": 'revenue',
    "Annual Sales": "revenue",
    "revenue": "revenue",

    "Square Footage": "sq_ft",
    "SqFt": "sq_ft",
    "Sq. Ft.": "sq_ft",
    "sqft": "sq_ft",
    "sq_ft": "sq_ft",

    # STATUS / FLAGS
    "Status Reason": "status_reason",
    "Operating Status": "operating_status",
    "Operation Status": "operating_status",
    "Open/Closed": "operating_status",
    "operating_status": "operating_status",

    "Active": "is_active",
    "Is Active": "is_active",
    "Active Flag": "is_active",
    "is_active": "is_active",

    # JURISDICTION / DISTRICTS
    "Service Area": "service_area",
    "Service Region": "service_area",
    "Jurisdiction": "jurisdiction",
    "Jurisdiction Name": "jurisdiction",
    "jurisdiction": "jurisdiction",
    "service_area": "service_area",

    "Community Board": "community_board",
    "community_board": "community_board",
    "Council District": "council_district",
    "council_district": "council_district",
    "Police Precinct": "police_precinct",
    "police_precinct": "police_precinct",
    "Assembly District": "assembly_district",
    "assembly_district": "assembly_district",
    "Senate District": "senate_district",
    "senate_district": "senate_district",

    "ID": "id",
    "Id": "id",
    "Identifier": "id",
    "Internal ID": "id",
    "Object ID": "id",
    "id": "id"
}

ALIASES: Dict[str, str] = dict(RAW_ALIASES)
NORMALIZED_ALIASES: Dict[str, str] = _normalize_aliases(RAW_ALIASES)
