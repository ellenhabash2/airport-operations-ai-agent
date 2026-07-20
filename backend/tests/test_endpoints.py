"""
Tests for the search and update endpoints.
"""


def test_search_flights_by_status(client):
    """The search endpoint filters by status."""
    response = client.get("/flights/search?status=delayed")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["count"] == 1
    assert payload["data"][0]["flight_number"] == "TA1000"


def test_search_flights_without_criteria_is_rejected(client):
    """An unfiltered search is refused."""
    response = client.get("/flights/search")

    assert response.status_code == 400


def test_search_flights_by_partial_airline(client):
    """The airline filter matches partially."""
    response = client.get("/flights/search?airline=test")

    assert response.get_json()["count"] == 2


def test_search_incidents_endpoint(client):
    """Incidents can be searched by free text."""
    response = client.get("/incidents/search?q=inspection")

    assert response.status_code == 200
    assert response.get_json()["count"] == 1


def test_search_incidents_without_keyword_is_rejected(client):
    """A search with no keyword is refused."""
    response = client.get("/incidents/search")

    assert response.status_code == 400


def test_update_flight_status_requires_a_token(client):
    """Write endpoints are not reachable anonymously."""
    response = client.patch("/flights/1/status", json={"status": "boarding"})

    assert response.status_code == 401


def test_update_flight_status(client, auth_headers):
    """A flight status can be changed through the API."""
    response = client.patch(
        "/flights/1/status", json={"status": "boarding"}, headers=auth_headers
    )
    payload = response.get_json()["data"]

    assert response.status_code == 200
    assert payload["previous_status"] == "delayed"
    assert payload["flight"]["status"] == "boarding"


def test_update_flight_status_rejects_invalid_value(client, auth_headers):
    """An unknown status is rejected with a 400."""
    response = client.patch(
        "/flights/1/status", json={"status": "landed"}, headers=auth_headers
    )

    assert response.status_code == 400


def test_update_status_of_a_missing_flight(client, auth_headers):
    """A flight that does not exist returns 404."""
    response = client.patch(
        "/flights/999/status",
        json={"status": "boarding"},
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_reassign_gate(client, auth_headers):
    """A flight can be moved to a free gate."""
    response = client.patch(
        "/flights/2/gate", json={"gate_number": "A02"}, headers=auth_headers
    )
    payload = response.get_json()["data"]

    assert response.status_code == 200
    assert payload["flight"]["gate_number"] == "A02"
    assert payload["released_gate"] == "B01"


def test_reassign_to_an_occupied_gate_conflicts(client, auth_headers):
    """Moving a flight to a busy gate returns 409."""
    response = client.patch(
        "/flights/1/gate", json={"gate_number": "B01"}, headers=auth_headers
    )

    assert response.status_code == 409


def test_update_runway_status(client, auth_headers):
    """Closing a runway reports the affected flights."""
    response = client.patch(
        "/runways/1/status", json={"status": "closed"}, headers=auth_headers
    )
    payload = response.get_json()["data"]

    assert response.status_code == 200
    assert payload["runway"]["status"] == "closed"
    assert payload["affected_flight_count"] == 2


def test_update_runway_status_rejects_invalid_value(client, auth_headers):
    """An unknown runway status is rejected."""
    response = client.patch(
        "/runways/1/status", json={"status": "flooded"}, headers=auth_headers
    )

    assert response.status_code == 400


def test_update_profile_changes_the_username(client, auth_headers):
    """The signed-in user can rename themselves."""
    response = client.patch(
        "/auth/me", json={"username": "controller"}, headers=auth_headers
    )

    assert response.status_code == 200
    assert response.get_json()["user"]["username"] == "controller"


def test_update_profile_requires_at_least_one_field(client, auth_headers):
    """An empty update is refused."""
    response = client.patch("/auth/me", json={}, headers=auth_headers)

    assert response.status_code == 400


def test_update_profile_rejects_a_short_password(client, auth_headers):
    """Passwords shorter than eight characters are refused."""
    response = client.patch(
        "/auth/me", json={"password": "short"}, headers=auth_headers
    )

    assert response.status_code == 400


def test_update_profile_rejects_a_taken_username(client, auth_headers):
    """A username already used by someone else causes a conflict."""
    client.post(
        "/auth/register",
        json={
            "username": "someone",
            "email": "someone@example.com",
            "password": "password123",
        },
    )
    response = client.patch(
        "/auth/me", json={"username": "someone"}, headers=auth_headers
    )

    assert response.status_code == 409


def test_new_password_works_for_login(client, auth_headers):
    """After a password change the new password is accepted."""
    client.patch(
        "/auth/me", json={"password": "newpassword123"}, headers=auth_headers
    )
    response = client.post(
        "/auth/login",
        json={"email": "tester@example.com", "password": "newpassword123"},
    )

    assert response.status_code == 200


def test_list_terminals(client):
    """The terminals endpoint reports gate availability per terminal."""
    response = client.get("/terminals")
    terminals = {t["name"]: t for t in response.get_json()["data"]}

    assert response.status_code == 200
    assert terminals["Terminal A"]["available_gates"] == 2
    assert terminals["Terminal B"]["available_gates"] == 0


def test_list_terminal_flights(client):
    """A terminal reports the flights using its gates."""
    response = client.get("/terminals/1/flights")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["count"] == 1
    assert payload["terminal"]["name"] == "Terminal A"
    assert payload["data"][0]["flight_number"] == "TA1000"


def test_flights_of_a_missing_terminal(client):
    """A terminal that does not exist returns 404."""
    response = client.get("/terminals/999/flights")

    assert response.status_code == 404


def test_index_lists_the_terminal_endpoints(client):
    """The service index advertises the terminal endpoints."""
    endpoints = client.get("/").get_json()["endpoints"]

    assert "GET /terminals" in endpoints
    assert "GET /terminals/<id>/flights" in endpoints