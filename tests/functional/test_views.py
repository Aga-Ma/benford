import json
import pytest

from app.constants import DATA_COLUMN_NAME


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200


def test_upload_files(client, upload_data):
    """
    GIVEN valid data file
    WHEN file posted
    THEN benford chart data returned
    """
    file_name = "fake-text-stream.txt"
    data = {
        'file': (upload_data, file_name)
    }
    response = client.post('/', data=data, follow_redirects=True,
                           content_type='multipart/form-data')
    response_data = json.loads(response.data.decode('utf8'))
    assert 'expected_values' in response_data
    assert 'found_values' in response_data
    assert 'labels' in response_data


@pytest.mark.parametrize(
    'invalid_file, expected_error_message',
    (
            (pytest.lazy_fixture("no_required_header"), "Main column header: {} not found".format(DATA_COLUMN_NAME.decode('utf8'))),
            (pytest.lazy_fixture("no_data"), "File is empty or not allowed column separators are used."),
            (pytest.lazy_fixture("invalid_data_type_file"),
             "All data in {} column should be a numeric type".format(DATA_COLUMN_NAME.decode("utf-8")))
    )
)
def test_invalid_data_file(client, invalid_file, expected_error_message):
    data = {
        'file': (invalid_file, "test.txt")
    }
    response = client.post('/', data=data, follow_redirects=True, content_type='multipart/form-data')
    assert expected_error_message in response.data.decode('utf8')
