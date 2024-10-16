import datetime
import os
import pandas as pd
from JMTracker.scrapper import AJOScrapper
from JMTracker.auxiliary import (
    corrupt_excel_reader, country_state_city_aggregator,
    validate_unique_id, validator_generator, validate_extension
)

"""
This file contains global setting for the project
and oher utility functions
"""

# global settings for the project
pwd = os.path.dirname(os.path.abspath(__file__))

settings = {
    # Paths
    'project_directory': pwd,
    'input_directory': os.path.abspath(os.path.join(pwd, '../inputs/')),
    'output_directory': os.path.abspath(os.path.join(pwd, '../output/')),
    'storage_directory': os.path.abspath(os.path.join(pwd, '../storage/')),
    # Project settings
    'today': datetime.date.today(),
    # Color theme for GUI (from PySimpleGui)
    'gui_theme': 'DarkTeal2',
    # Custom setting path
    'custom_settings': os.path.abspath(os.path.join(pwd, '../custom_settings.py')),
    # Decide whether custom input settings are overriden or appended
    'custom_overrides_default': False,
}

# == Input Type Configuration === #
"""
The following options determine where we get information from and how process
it.


Required Columns:
-----------------
The system requires the following columns in any input file:
 - origin_id: an integer indexing the listings. This should be a unique
          identifier of a posting within a system.
 - title: the title of the posting
 - location: the location of the posting
 - institution: the name of the institution
 - deadline: the application deadline in year-month-day
 - url: the url to the full posting

Optional Columns:
-----------------
Besides these, the system also stores any column given a name in the renaming
rules, unless explicitly included in the "to_drop" list. The following columns
are also shown to users, if they exist:
    - section, division, department, keywords, full_text

Column Generators:
------------------
If, after renaming some of the required or optional columns are missing, the system
will see if a generator missing exist. This generator should have a key
equal to {column name}_generator and should be a function that takes a row
of the data and the dataframe of postings already included (or None if its the
first usage) and return a value for the row.

Important:
----------
the following column names are protected and will be overwritten
even if present in the data:
# FIXME: finish this
"origin", "status", "updated", ...

Also, 'origin' must be unique across sources.



See the example below for more details

"""

input_option_settings = [
    {
        # The origin file
        'origin': 'AEA',
        # The url to link to for file download
        'download_url': 'https://www.aeaweb.org/joe/listings?issue=2024-02',
        # Excepcted extension, lower-case no period
        'expected_extension': 'xlsx',
        # Instructions to show user
        'download_instructions': 'download the "native xlx" file, do not modify',
        # A validator for the path given for the file to load
        'url_validator': validator_generator(
            [validate_extension], 'AEA', [('xlsx', 'AEA')]
        ),
        # name of the file to use to store the latest version in the inputs
        'input_file_name': 'latest_aea.xlsx',
        # input loader. A function that takes the url and returns the
        # dataframe
        'loader': corrupt_excel_reader,
        # A validator function to run on the file after loaded. This function
        # should return two things: status (bool, True indicates all is good),
        # message (str, popup message in case of failure).
        'validator': validator_generator(
            [validate_unique_id], 'AEA', [('jp_id', 'AEA')]
        ),
        # Column rename rules
        'renaming_rules': {
            'jp_id': 'origin_id',
            'jp_section': 'section',
            'jp_institution': 'institution',
            'jp_division': 'division',
            'jp_department': 'department',
            'jp_keywords': 'keywords',
            'jp_title': 'title',
            'jp_full_text': 'full_text',
            'jp_salary_range': 'salary_range',
            'locations': 'location',
            'Application_deadline': 'deadline'
        },
        # if a url column is not available, will default to this behavior. This
        # is a function that receives the row and should return a string with
        # the url to see the posting. Note that we dont use the second argument
        # which contains all the postings already loaded into the system.
        'url_generator': (
            lambda x, y: 'https://www.aeaweb.org/joe/listing.php?JOE_ID=' +
            "{:d}".format(x['origin_id']))
    },
    {
        'origin': 'EJM',
        'download_url': 'https://econjobmarket.org/users/positions/download/a',
        'expected_extension': 'csv',
        # A validator for the path given for the file to load
        'url_validator': validator_generator(
            [validate_extension], 'EJM', [('csv', 'EJM')]
        ),
        'input_file_name': 'latest_ejm.csv',
        'validator': validator_generator(
            [validate_unique_id], 'EJM', [('Id', 'EJM')]
        ),
        'download_instructions': (
            'download the CSV file. Careful to download all'
            'postings if this is your first time using this app but not the first '
            'time using EJM.'
        ),
        'loader': lambda x: pd.read_csv(x, header=1),
        'renaming_rules': {
            'Id': 'origin_id',
            'URL': 'url',
            'Ad title': 'title',
            'Types': 'section',
            'Categories': 'division',
            'Deadline': 'deadline',
            'Department': 'department',
            'Institution': 'institution',
            'City': 'city',
            'State/province': 'state',
            'Country': 'country',
            'Application method': 'application_method',
            'Application URL': 'application_url',
            'Application email': 'application_email',
            'Ad text (in markdown format)': 'full_text'
        },
        # If location is not available, defaults to this generator
        'location_generator': country_state_city_aggregator,
        # list of columns renames that we dont want to store
        'to_drop': ['city', 'state', 'country'],
    },
    {
        'origin': 'AJO',
        'download_url': None,
        'download_action': AJOScrapper.gui_scrape,
        'expected_extension': 'csv (Warning: this is still in beta.)',
        'url_validator': None,
        'input_file_name': None,
        'validator': validator_generator(
            [validate_unique_id], 'AJO', [('origin_id', 'AJO')]
        ),
        'download_instructions': (
            'Click on the download link to scrape AJO.\n'
            ' === Please review any deadlines === \n. This is still in beta.'
        ),
        'loader': pd.read_csv,
        'renaming_rules': {}
    }
]


# Pandas configuration
pd.options.display.max_columns = 300
pd.options.display.max_rows = 100
pd.options.display.width = 150
