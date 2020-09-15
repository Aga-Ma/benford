import pytest
from app.benford_chart import DataValidator, InvalidDataFormat
from app.constants import DATA_COLUMN_NAME


def test_data_valid(valid_data):
    """
    GIVEN valid data
    WHEN validation executed
    THEN no errors nor warnings were collected
    """
    dv = DataValidator(valid_data)
    assert dv.is_valid() is True
    assert dv.errors == []
    assert dv.warnings == []


def test_required_column_missing(no_required_header_data):
    """
    GIVEN data without required header
    WHEN validation executed
    THEN InvalidDataFormat exception was raised
    """
    with pytest.raises(InvalidDataFormat):
        dv = DataValidator(no_required_header_data)
        dv.is_valid(raise_errors=True)


def test_errors_collected(no_required_header_data):
    """
    GIVEN data without required header
    WHEN validation executed
    THEN errors collected
    """
    dv = DataValidator(no_required_header_data)
    dv.is_valid(raise_errors=False)
    assert dv.errors


def test_corrupted_data_removed(data_missing_in_rows):
    """
    GIVEN data with different number of items in rows
    WHEN validation executed
    THEN warnings collected
    """
    dv = DataValidator(data_missing_in_rows)
    dv.is_valid()
    validated_data = [[item.strip() for item in row] for row in dv.validated_data]
    assert validated_data == [[b'State', b'Town', b'7_2009', b'3', b'4', b'8.40188'],
                              [b'Alabama', b'Abbeville', b'2930', b'3', b'10', b'3.94383'],
                              [b'Alabama', b'Addison', b'709', b'3', b'8', b'lip.9844'],
                              [b'Alabama', b'Akron', b'433', b'3', b'6', b'']]


def test_warning_collected(data_missing_in_rows):
    """
    GIVEN data with different number of items in rows
    WHEN validation executed
    THEN warnings collected
    """
    dv = DataValidator(data_missing_in_rows)
    dv.is_valid(raise_errors=False)
    assert dv.warnings


def test_no_data_to_analyze(headers_only):
    """
    GIVEN data headers only
    WHEN validation executed
    THEN "No data to analyze" msg in exception
    """
    with pytest.raises(InvalidDataFormat) as e:
        dv = DataValidator(headers_only)
        dv.is_valid(raise_errors=True)
    assert "No data to analyze" in str(e.value)


def test_empty_file(empty_file):
    """
    GIVEN empty file
    WHEN validation executed
    THEN "File is empty" msg in exception
    """
    with pytest.raises(InvalidDataFormat) as e:
        dv = DataValidator(empty_file)
        dv.is_valid(raise_errors=True)
    assert "File is empty or not allowed column separators are used. " \
           "Expected column separator for given file format: {}".format(dv.delimiter) in str(e.value)


def test_wrong_data_type(invalid_data_type):
    """
    GIVEN not numeric type data in required column
    WHEN validation executed
    THEN "File is empty" msg in exception
    """
    with pytest.raises(InvalidDataFormat) as e:
        dv = DataValidator(invalid_data_type)
        dv.is_valid(raise_errors=True)
    assert "All data in {} column should be a numeric type".format(DATA_COLUMN_NAME.decode("utf-8")) in str(e.value)


def test_repeated_header(required_header_repeated):
    """
    GIVEN data with required header repeated
    WHEN validation executed
    THEN warnings collected
    """
    dv = DataValidator(required_header_repeated)
    dv.is_valid(raise_errors=False)
    assert "More than one column with required header found. Data are going to be collected from first one" in dv.warnings
