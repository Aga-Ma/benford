import re

import benford as bf
import functools
import pandas
from werkzeug.datastructures import FileStorage

from app.constants import DATA_COLUMN_NAME


class InvalidDataFormat(ValueError):
    """Data does not conform to expected format"""

    def __init__(self, err: list):
        self.err = err

    def __str__(self):
        return "Data could not be analyze. Following critical errors found: {}".format(" ".join(self.err))


class DataFormat:

    def __init__(self, file_extension: str):
        self.delimiter = b';' if file_extension == ".csv" else b'\t'
        self.extension = file_extension


class DataValidator(DataFormat):

    def __init__(self, data: bytes, file_extension: str = ""):
        super().__init__(file_extension)
        self.data = data
        self._errors = []
        self._warnings = []
        self._validated = False
        self._split_data = None
        self._headers = None

    @property
    def errors(self):
        if not self._validated:
            msg = 'You must call `.is_valid()` before accessing `.errors`.'
            raise AssertionError(msg)
        return self._errors

    @property
    def warnings(self):
        if not self._validated:
            msg = 'You must call `.is_valid()` before accessing `.warnings`.'
            raise AssertionError(msg)
        return self._warnings

    def is_valid(self, raise_errors=True):
        """
        Verifies data correctness.
        :param raise_errors: bool
        :return: bool if exception weren't raise previously
        """
        self._do_validation()
        self._validated = True
        if raise_errors and self._errors:
            raise InvalidDataFormat(self._errors)
        return False if self._errors else True

    def _do_validation(self):
        """
        Calling all verification methods. Removes all data rows that does not match number of columns defined by
        number of headers.
        :return: None
        """
        self._data_can_be_split()
        if self._split_data:
            if self._main_column_present() and self._any_data_to_analyze():
                self._data_type_correct()
                self._headers_match_columns()
                self.validated_data = [data_row for index, data_row in enumerate(self._split_data)
                                       if index not in self.__data_corrupted]

    def _data_can_be_split(self):
        """
        Checks if data can be split to separate columns for each line.
        :return: bool
        """
        try:
            self._split_data = [row.split(self.delimiter) for row in self.data.splitlines()]
            self._headers = [header.strip() for header in self._split_data[0]]
        except (IndexError, AttributeError):
            self._errors.append("File is empty or not allowed column separators are used. "
                                "Expected column separator for given file format: {}".format(self.delimiter))
            return False
        return True

    def _main_column_present(self):
        """
        Checks if required column with data to be analyzed exists by verifying if it is present in first row of split
        data.
        :return: bool
        """
        if DATA_COLUMN_NAME not in self._split_data[0]:
            self._errors.append("Main column header: {} not found".format(DATA_COLUMN_NAME.decode("utf-8")))
            return False
        return True

    def _any_data_to_analyze(self):
        """
        Checks if data contains any data to analyze by verifying if there is more than single headers row.
        :return: bool
        """
        if len(self._split_data) <= 1:
            self._errors.append("No data to analyze")
            return False
        return True

    def _data_type_correct(self):
        """
        Checks if data in expected column are or can be map to numerical type as only numeric data can be analyzed.
        :return: bool
        """
        filtered_data = self._get_required_column_data()
        try:
            list(map(int, filtered_data))
        except ValueError:
            self._errors.append(
                "All data in {} column should be a numeric type".format(DATA_COLUMN_NAME.decode("utf-8")))
            return False
        return True

    def _get_required_column_data(self):
        index = self._get_required_data_column_index()
        data = []
        for data_row in self._split_data[1:]:
            try:
                data.append(data_row[index])
            except IndexError:
                continue
        return data

    def _get_required_data_column_index(self):
        """
        Checks whether there is more than one column with required header.
        :return: list of indexes for required column
        """
        required_col_number = self._headers.count(DATA_COLUMN_NAME)
        if required_col_number > 1:
            self._warnings.append("More than one column with required header found. "
                                  "Data are going to be collected from first one")
        return self._headers.index(DATA_COLUMN_NAME)

    def _headers_match_columns(self):
        """
        Checks if number of data in each row match number of columns.
        :return: bool
        """
        data_corrupted = self.__data_corrupted
        if data_corrupted:
            self._warnings.append("Number of headers: {} is not equal to number of data in each row. "
                                  "Rows: {} are going to be omitted".format(len(self._headers),
                                                                            data_corrupted))
            return False
        return True

    @property
    @functools.lru_cache()
    def _row_length(self):
        """
        Create a dict of row numbers as keys and number of data in each row as values.
        :return: dict
        """
        items_in_a_row = map(len, self._split_data)
        return dict(list(enumerate(items_in_a_row)))

    @property
    @functools.lru_cache()
    def __data_corrupted(self):
        """
        Get list of row numbers for rows with different amount of data than number of headers by compering rows and
        headers items amount. Can return an empty list if the data amount was consistent
        :return: list
        """
        num_of_headers = len(self._headers)
        return [row_ind for row_ind in self._row_length if self._row_length[row_ind] != num_of_headers]


class BenfordData(DataFormat):

    def __init__(self, data_file: FileStorage, file_extension: str = ""):
        super().__init__(file_extension)
        self.data = data_file.read()
        self.file_extension = file_extension
        dv = DataValidator(self.data, self.file_extension)
        dv.is_valid()
        self.validated_data = dv.validated_data

    @property
    def benford_data(self):
        """Performs the Benford First Digits test on the series of data provided"""
        bnf = bf.first_digits(self._get_benford_data(), digs=1, show_plot=False)
        return bnf

    def _get_benford_data(self):
        """Converts bytes data from data_file to numeric data for required data column. Benford First Digits test
        requires numeric data for analysis"""
        return pandas.to_numeric(self.data_frames[DATA_COLUMN_NAME])

    @property
    def data_frames(self):
        """Constructing pandas DataFrame for all validated data given in data_file"""
        return pandas.DataFrame(self.validated_data[1:], columns=self.validated_data[0])


class Chart:

    def __init__(self, data):
        self.chart_data = data

    @property
    def labels(self):
        """Chart yAxis labels"""
        return self.chart_data.index.to_frame()['First_1_Dig'].to_dict()

    @property
    def expected(self):
        """Expected first digits distribution data"""
        return self.chart_data['Expected'].to_dict()

    @property
    def found(self):
        """Calculated first digits distribution data"""
        return self.chart_data['Found'].to_dict()
