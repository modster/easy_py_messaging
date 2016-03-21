#!/bin/env python
import sys
import json
import utils

"""
    Read a log file, apply user provided function for filtering.
    With this base class CSV and JSON can result.

    Further filtering such as WARNING and higher levels could
    be filtered from the cruft.
"""

# The parameters controlling log filtering.
LogFilters = {
        'in_file_handle': sys.stdin,   # Default input is stdin
        'out_file_handle': sys.stdout, # Default: stdout
        'level': 'DEBUG',              # Default: All logs entries
        'out_format': 'JSON',          # Default format
        'out_file': None,              # Printable output filename
        'in_file': None,               # printable intput filename
        'start_secs': 0,                 # start and end dates.
        'start': None,                 # start and end dates.
        'end_secs': sys.maxint,
        'end': None,
        'line_number': 0,              # Log line # in input file.
        'sep_char':    utils.PAYLOAD_CONNECTOR,
        'key_val_sep': utils.KEY_VALUE_SEPARATOR,
}

class LogFilter(object):
    """
    Base class for user provided filters.

    Give an input line, return a dictionary with the input parsed.

    Special keywords:

    DATE = the 1st portion with the ISO8601 date.

    level = Level of the log: DEBUG, INFO, ...

    The payload, the last part of the log, gets parsed and the dictionary
    contains the provided keyword and values.

    filter_level = Lowest file output. Lesser levels get ignored.
        For example, filter_level="WARNING" ignored DEBUG and INFO levels.

    Suggested use:
        * The data should contain the same keywords on each line.
        * The first output would list the keywords for a spreadsheet
        * Don't forget to list the data for the first line.
        * Each additional line lists data

    filter_fcn = filtering function to determine
    if and what gets output. The signature:
        filter_fcn(log_entry_dict, line_number)
    This function returns a possibly changed
    dictionary that will be converted to JSON
    for outputting or None indicating this
    entry gets ignored.

    If filter_fcn == None, then nothing will 
    gets called.

    A user should examine the relevant entries in
    log_entry_dict. Depending upon desired effects,
    keys may be deleted, values modified or the
    entire log entry declared irrelevant by
    returning None.

    After scanning the single log entry dictionary,
    the possibly modified dictionary should be
    returned or return None if the entry should
    be ignored.
    """

    def __init__(self, log_filters, filter_fcn = None):
        self.log_filters = log_filters
        self.filter_fcn = filter_fcn
        self.normalize_config()
        self.filter_level = log_filters['level']
        self.filter_dict = utils.filterPriority(self.filter_level)
        self.sep_char = log_filters['sep_char']
        self.key_val_sep = log_filters['key_val_sep']
        self.start_secs = log_filters['start_secs']
        self.end_secs = log_filters['end_secs']
        self.log_entry = ''
        self.log_dict = {}
        # Current line number in input file.
        self.line_number = self.log_filters['line_number']

    def normalize_config(self):
        """
        Some data may be missing. Verify a working set
        of parameters.
        """
        if 'start' not in self.log_filters.keys():
            self.log_filters['start'] = '1970-01-01T00:00:00.000'
        if 'start_secs' not in self.log_filters.keys():
            start_secs = utils.ISO8601ToSeconds(self.log_filters['start'])
            if start_secs == None:
                sys.stderr.write('Configuraton: Invalid start time:"%s"\n' % self.log_filters['start'])
                sys.exit(1)
            self.log_filters['start_secs'] = start_secs

        if 'end' not in self.log_filters.keys():
            # No end time specified. Assume now
            now_secs = utils.timeNow()
            self.log_filters['end_secs'] = now_secs
            self.log_filters['end'] = utils.secondsToISO8601(now_secs)
        if 'end_secs' not in self.log_filters.keys():
            end_secs = utils.ISO8601ToSeconds(self.log_filters['end'])
            if end_secs == None:
                sys.stderr.write('Configuraton: Invalid end time:"%s"\n' % self.log_filters['end'])
                sys.exit(1)
            self.log_filters['end_secs'] = end_secs

        if 'sep_char' not in self.log_filters.keys():
            self.log_filters['sep_char'] = utils.SEPARATION_CHAR
        if 'key_val_sep' not in self.log_filters.keys():
            self.log_filters['key_val_sep'] = utils.KEY_VALUE_SEPARATOR
        if 'payload_connector' not in self.log_filters.keys():
            self.log_filters['payload_connector'] = utils.PAYLOAD_CONNECTOR

        if 'level' not in self.log_filters.keys():
            self.log_filters['level'] = 'DEBUG' # Pass all logs

        if 'line_number' not in self.log_filters.keys():
            self.log_filters['line_number'] = 0



    def parse_log_entry(self, log_entry):
        """
        Break the log entry into small pieces and place results into log_dict
        Returns the log dictonary of the pieces of the log entry.
        """
        self.log_entry = log_entry
        self.line_number += 1
        if log_entry == '':
            # Returning None provides a convenient loop
            # termination. This assumes that the data files
            # contain no blank lines!
            return None     # Common at end of file
        try:
            date, level, payload = self.log_entry.split('\t')
        except ValueError as err:
            sys.stderr.write('ERROR: "%s", line#%d, Log line: "%s"\n' % \
                    (str(err), self.line_number, self.log_entry))
            self.log_dict = {'ERROR': '"""' + str(err) + '"""',
                    'LOG': str(self.log_entry)}
            return None


        # Does this log meet the log_filter level desired?
        if level in self.filter_dict.keys():   # Ignore if level gets ignored.
            self.log_dict['level'] = level
        else:
            return None     # This level to be ignored.

        self.log_dict['date'] = date
        self.log_seconds = utils.ISO8601ToSeconds(date)
        date_within = self.within_dates(self.log_seconds)
        if date_within != True:  # date_with could be False or None
            return None

        self.parse_payload(payload)

        if self.filter_fcn:
            # User has provided a filter fcn.
            return self.filter_fcn(self.log_dict, self.line_number)
        else:
            # No user provided filter fcn.
            return self.log_dict


    def parse_payload(self, payload):
        """
        Parse the payload.
        """
        items = payload.split(self.sep_char)
        for item in items:
            if len(item) == 0:
                # Ignore empty item.
                # An example:    name=value&&name1=value1
                # The double '&&' results in an empty item.
                continue    
            try:
                key, value = item.split(self.key_val_sep)
            except ValueError as err:
                sys.stderr.write(('ERROR: "%s", line#:%d, ' + \
                        'key=value: "%s" Line:%s\n') % \
                        (str(err), self.line_number, item, self.log_entry))
                continue    # Ignore this entry
            # Duplicate keys get ignored.
            self.log_dict[key] = value

    def within_dates(self, log_seconds):
        """
        Determines if the log date falls within requested
        boundaries.

        log_seconds = Date of log in seconds since epoch.

        Return: True if log date is within start and end dates.
                False if not within date boundaries.
                None iF invalid log_date_str.
        """

        if log_seconds == None:
            return None
        if self.log_filters['start_secs'] <= log_seconds <= self.log_filters['end_secs']:
            return True
        return False


class LogFilterCSV(LogFilter):
    """
        For CSV, assume a log file contains exactly the
        same payload format for each log line. 

        Our log files will contain multiple temperature sources:
            inside=65.2     # Temp inside house
            patio=73.2      # Temp under patio roof
            sun=79.3        # Temp in sun

        A typical log entry would be:
            2016-03-10T09:01:22.808\tINFO\tinside=65.2,patio=73.2,sun=79.3,host=brass

        This gets displayed without the tabs appearing:
            2016-03-10T09:01:22.808 INFO inside=65.2,patio=73.2,sun=79.3,host=brass
        
        Each field gets separated by tabs.

        The "host=brass" at the end of the payload gets appened automatically
        by the sender of the log. Easily finding the system of the orignal
        log eases possible problems.

        CSV Notes
        ============
        Using CSV as an output format implies that each line contains
        the same fields. Data lines that use different keys will report
        different data for the same column.

    """
        
    def __init__(self, log_filters, filter_fcn=None):
        super(LogFilterCSV, self).__init__(log_filters, filter_fcn)

    def log_keys(self):
        """
        Create 1st line of keywords
        The user passes the data dictionary because
        the user filter fcn may have modified it.
        """
        output = ''
        for key in sorted(self.log_dict):
            output += key + ','
        output = output[:-1]
        return output
        
    def log_data(self):
        """
        Create a single data entry and return it
        The user passes the data dictionary because
        the user filter fcn may have modified it.
        """
        output = ''
        for key in sorted(self.log_dict):
            try:
                output += self.log_dict[key] + ','
            except Exception as err:
                sys.stderr.write('line#%d: %s\n' % (self.line_number, str(err)))
        output = output[:-1]
        return output


class LogFilterJSON(LogFilter):
    """
        JSON output provides a standard JSON syntax. Both keys and value
        become double quoted.
    """

    def __init__(self, log_filters, filter_fcn=None):
        super(LogFilterJSON, self).__init__( log_filters, filter_fcn)

    def log_2_JSON(self):
        # Return the data dictionary as JSON. 
        return json.dumps(self.log_dict)

    def log_file_2_JSON_handler(self, fh):
        """
        Same as logFileToJSON except a file
        handle gets passed instead of a filename.
        """
        outline = '['
        line_number = 0
        for line in fh:
            self.log_dict = {}    # Wipe out previous values
            line_number += 1
            try:
                line = line.strip('\n')
                self.log_entry = line
                self.log_dict = self.parse_log_entry(line)
            except Exception:
                # Bad input. Lower levels have already reported.
                continue    # Ignore.
            # This log level is to low to consider if == None
            if self.log_dict == None:
                continue
            outline += json.dumps(self.log_dict) + ','

        outline = outline[:-1]
        outline += ']'
        return outline

    def log_file_2_JSON(self, filename):
        """
        Given a log filename of logging data, return
        an array of log dictionaries. Each log entry
        becomes a JSON dictioary.

        filter_fcn = filtering function to determine
        if and what gets output. The signature:
            filter_fcn(log_entry_dict, line_number)
        This function returns a possibly changed
        dictionary that will be converted to JSON
        for outputting or None indicating this
        entry gets ignored.
        If filter_fcn == None, then nothing will 
        gets called.

        Return: array of JSON objects.

        Errors: Invalid filename returns None
        """
        try:
            fh = open(filename, 'r')
        except IOError as err:
            sys.stderr.write('%s: %s\n' % (filename, str(err)))
            return None
        return self.log_file_2_JSON_handler(fh)


