from datetime import date
from pathlib import Path
from freezegun import freeze_time

import pytest
import requests


def get_test_data_path(filename):
    return Path(__file__).parent / "test_data" / filename


def read_file(filename):
    return get_test_data_path(filename).read_text()

@pytest.fixture
def mock_success_req(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = mocker.Mock()
    mock_response.text = read_file("html_check_test.html")
    mocker.patch('requests.get', return_value=mock_response)
    return mock_response

@pytest.fixture
def mock_fail_req(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 400
    mock_response.raise_for_status = mocker.Mock()
    http_error = requests.HTTPError("404 Not Found")
    mock_response.raise_for_status.side_effect = http_error
    mocker.patch('requests.get', return_value=mock_response)
    return mock_response


@pytest.fixture
def mock_date():
    def _mock(fake_date):
        return freeze_time(fake_date.isoformat())
    return _mock
    
    
def test_save(repo):
    url = {"name": "https://www.example.com"}
    repo.save(url)
    assert "id" in url
    assert url["name"] == "https://www.example.com"


def test_find_exist(repo):
    url = {"name": "https://www.test.com"}
    repo.save(url)
    id = url["id"]
    found = repo.find(id)
    assert found is not None
    assert found["id"] == id
    assert found["name"] == "https://www.test.com"


def test_find_None(repo):
    id = -1
    url = repo.find(id)
    assert url is None


def test_get_content_no_checks(repo):
    urls = [{"name": "https://www.test1.com"},
            {"name": "https://www.test2.com"}, 
            {"name": "https://www.test3.com"}
            ]
    ids = []
    for url in urls:
        repo.save(url)
        ids.append(url["id"])

    urls_result = repo.get_content()
    assert len(urls_result) == 3
    for i, item in enumerate(urls_result):
        assert item["id"] == ids[i]
        assert item["name"] == urls[i]["name"]
        assert item["last_date"] is None
    id_from_result = [item["id"] for item in urls_result]
    assert id_from_result == sorted(id_from_result)


def test_does_exist_true(repo):
    url = {"name": "https://www.test4.com"}
    repo.save(url)
    id = url["id"]
    result = repo.does_exist(url)
    assert result is True
    assert url["name"] == "https://www.test4.com"
    assert url["id"] == id


def test_does_exist_false(repo):
    url = {"name": "https://www.test5.com"}
    repo.save(url)
    wrong = {"name": "https://www.wrong.com"}
    result = repo.does_exist(wrong)
    assert result is False
    assert "id" not in wrong


def test_check_200(repo, mock_success_req):
    url = {"name": "https://www.test6.com"}
    repo.save(url)

    repo.check(url)
    
    checks = repo.get_check_content(url)
    assert len(checks) == 1
    assert checks[0]["status_code"] == 200
    assert checks[0]["h1"] == "Test"
    assert checks[0]["title"] == "Document"
    assert checks[0]["description"] == "valuable text"


def test_check_400(repo, mock_fail_req):
    url = {"name": "https://www.test7.com"}
    repo.save(url)

    with pytest.raises(requests.HTTPError):
        repo.check(url)
    
    checks = repo.get_check_content(url)
    assert len(checks) == 0


def test_get_check_content_exist(repo, mock_success_req):
    url = {"name": "https://www.test8.com"}
    repo.save(url)
    for i in range(3):
        repo.check(url)

    result = repo.get_check_content(url)
    assert len(result) == 3
    for item in result:
        assert item["h1"] == "Test"
        assert item["title"] == "Document"
        assert item["description"] == "valuable text"
        assert item["url_id"] == url["id"]
        assert item["status_code"] == 200


def test_get_content_with_checks(repo, mock_success_req, mock_date):
    urls = [{"name": "https://www.test1.com"},
            {"name": "https://www.test2.com"}, 
            {"name": "https://www.test3.com"}
            ]
    ids = []

    for url in urls:
        repo.save(url)
        ids.append(url["id"])

    for url in urls:
        with mock_date(date(2025, 10, 11)):
            repo.check(url)
        
        with mock_date(date(2021, 10, 11)):
            repo.check(url)
    urls_result = repo.get_content()
    assert len(urls_result) == 3
    for i, item in enumerate(urls_result):
        assert item["id"] == ids[i]
        assert item["name"] == urls[i]["name"]
        assert item["last_date"] == date(2025, 10, 11)
        assert item["status_code"] == 200
    id_from_result = [item["id"] for item in urls_result]
    assert id_from_result == sorted(id_from_result)
