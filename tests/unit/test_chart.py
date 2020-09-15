from io import BytesIO
from werkzeug.datastructures import FileStorage
from app.benford_chart import Chart, BenfordData

data_storage = FileStorage(filename="test")
data_storage.stream = BytesIO(b"""7_2009
                                   0
                                   0
                                   0
                                   0""")


def chart():
    bfd = BenfordData(data_storage).benford_data
    return Chart(data=bfd)


bf_chart = chart()
bf_first_digit_distribution = {1: 0.301,
                               2: 0.176,
                               3: 0.125,
                               4: 0.097,
                               5: 0.079,
                               6: 0.067,
                               7: 0.058,
                               8: 0.051,
                               9: 0.046}


def test_labels():
    assert bf_chart.labels == {dig: dig for dig in range(1, 10)}


def test_found():
    assert bf_chart.found == {dig: 0.0 for dig in range(1, 10)}


def test_expected():
    assert {k: round(v, 3) for k, v in bf_chart.expected.items()} == bf_first_digit_distribution
