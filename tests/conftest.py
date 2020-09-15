from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage

from app import app as flask_app


@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


data_storage = FileStorage(filename="test")


@pytest.fixture
def upload_data():
    return BytesIO(b"""State	Town	7_2009	3	4	8.40188
                       Alabama	Abbeville 	2930	3	10	3.94383
                       Alabama	Adamsville 	4782	3	11	7.83099
                       Alabama	Addison 	709	3	8	lip.9844
                       Alabama	Akron 	433	3	6	9.11647""")


@pytest.fixture
def valid_data_file_storage(upload_data):
    data_storage.stream = upload_data
    return data_storage.stream


@pytest.fixture
def valid_data():
    data_storage.stream = BytesIO(b"""State	Town	7_2009	3	4	8.40188
                                   Alabama	Abbeville 	2930	3	10	3.94383
                                   Alabama	Adamsville 	4782	3	11	7.83099
                                   Alabama	Addison 	709	3	8	lip.9844
                                   Alabama	Akron 	433	3	6	9.11647""")
    return data_storage.read()


@pytest.fixture
def no_required_header():
    return BytesIO(b"""State	Town	    TEST	3	4	8.40188
                       Alabama	Abbeville 	2930	3	10	3.94383
                       Alabama	Adamsville 	4782	3	11	7.83099
                       Alabama	Addison 	709	    3	8	lip.9844
                       Alabama	Akron 	    433	    3	6	9.11647""")


@pytest.fixture
def no_required_header_data(no_required_header):
    data_storage.stream = no_required_header
    return data_storage.read()


@pytest.fixture
def data_missing():
    return BytesIO(b"""State	    Town	7_2009	3	4	8.40188
                      Alabama	Abbeville 	2930	3	10	3.94383
                      Alabama	4782	3	11	7.83099
                      Alabama	Addison 	709	3	8	lip.9844
                      Alabama	Akron 	433	3	6	""")


@pytest.fixture
def data_missing_in_rows(data_missing):
    data_storage.stream = data_missing
    return data_storage.read()


@pytest.fixture
def headers_only():
    data_storage.stream = BytesIO(b"Test1	Test2	7_2009	Test_3")
    return data_storage.read()


@pytest.fixture
def no_data():
    return BytesIO(b"")


@pytest.fixture
def empty_file(no_data):
    data_storage.stream = no_data
    return data_storage.read()


@pytest.fixture
def invalid_data_type_file():
    return BytesIO(b"""7_2009
                       A
                       B
                       C
                       D""")


@pytest.fixture
def invalid_data_type(invalid_data_type_file):
    data_storage.stream = invalid_data_type_file
    return data_storage.read()


@pytest.fixture
def required_header_repeated():
    data_storage.stream = BytesIO(b"""7_2009	Town	    7_2009	3	  7_2009
                                      1	        Adamsville 	4    	3	  7
                                      2	        Addison 	5	 	3     8
                                      3	        Akron 	    6	 	3     9""")
    return data_storage.read()
