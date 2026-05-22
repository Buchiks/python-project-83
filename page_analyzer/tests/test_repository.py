import pytest
import requests
from datetime import date


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
    assert url == None

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

def test_check_200(repo, mocker):
    url = {"name": "https://www.test6.com"}
    repo.save(url)

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch('requests.get', return_value=mock_response)

    repo.check(url)

    with repo.conn.cursor() as cur:
        cur.execute(
            "SELECT status_code FROM url_checks WHERE url_id = %s",
            (url["id"],)
        )
        result = cur.fetchone()
        assert result is not None
        assert result[0] == 200
    
def test_check_400(repo, mocker):
    url = {"name": "https://www.test7.com"}
    repo.save(url)

    mock_response = mocker.Mock()
    mock_response.status_code = 400
    mock_response.raise_for_status = mocker.Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    mocker.patch('requests.get', return_value=mock_response)

    with pytest.raises(requests.HTTPError):
        repo.check(url)
    
    with repo.conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM url_checks WHERE url_id = %s",
            (url["id"],)
        )
        count = cur.fetchone()[0]
        assert count == 0

def get_check_content_exist(repo):
    url = {"name": "https://www.test8.com"}
    repo.save(url)
    with repo.conn.cursor() as cur:
        for i in range(3):
            cur.execute(
                "INSERT INTO url_checks (url_id, status_code) VALUES(%s, %s)", (url["id"], 200,)
            )

    result = repo.get_check_content(url)
    assert len(result) == 3
    for item in result:
        assert item["url_id"] == url["id"]
        assert item["status_code"] == 200

def test_get_content_with_checks(repo):
    urls = [{"name": "https://www.test1.com"},
            {"name": "https://www.test2.com"}, 
            {"name": "https://www.test3.com"}
            ]
    ids = []

    for url in urls:
        repo.save(url)
        ids.append(url["id"])
    with repo.conn.cursor() as cur:
        for i in range(3):
            cur.execute(
                "INSERT INTO url_checks (url_id, status_code, created_at) VALUES(%s, %s, %s)", (ids[i], 200, "2025-10-11")
            )
            cur.execute(
                "INSERT INTO url_checks (url_id, status_code, created_at) VALUES(%s, %s, %s)", (ids[i], 200, "2021-10-11")
            )
            
    urls_result = repo.get_content()
    assert len(urls_result) == 3
    for i, item in enumerate(urls_result):
        assert item["id"] == ids[i]
        assert item["name"] == urls[i]["name"]
        assert item["last_date"] == date(2025, 10, 11)
        assert item["status_code"] == 200
    id_from_result = [item["id"] for item in urls_result]
    assert id_from_result == sorted(id_from_result)
