"""
Exercise 04 — Mocking External Calls with unittest.mock     [Tier: ★ Core]
Chapter 31 · Pattern: Mock / patch / side_effect / autospec · Target time: 30 min

Problem
-------
A heat-alert job asks a weather service for each city's temperature and notifies an on-call
address when a city is at or above a threshold. Two pieces of code talk to the outside world:

* ``fetch_temperature(city, base_url)`` calls ``urlopen`` and parses JSON ``{"temp_c": 31.5}``.
* ``check_heat_alerts(cities, get_temp, notifier, threshold)`` takes its collaborators as
  arguments (dependency injection). A city whose lookup raises ``ConnectionError`` is reported
  as ``"<city>: unavailable"`` and must not stop the job.

Implement both and test them without the network: inject ``Mock`` objects into
``check_heat_alerts`` and ``patch`` ``urlopen`` where ``fetch_temperature`` looks it up.

Examples
--------
>>> notifier = Mock()
>>> check_heat_alerts(["Pune", "Oslo"], {"Pune": 38.0, "Oslo": 9.0}.get, notifier, 35.0)
['Pune']
>>> notifier.send.call_args
call('oncall@example.com', 'Heat alert: Pune at 38.0C')

Constraints
-----------
- No real network access in tests. Tests must run in milliseconds.

Approach ladder
---------------
1. Brute force — call the real API in tests: slow, flaky, needs keys, cannot test outages.
2. Improved   — ``patch`` everything by module path; works but couples tests to import layout.
3. Optimal    — inject collaborators (``get_temp``, ``notifier``) so tests pass simple fakes or
   ``Mock(spec=...)``; reserve ``patch`` for the thin edge that touches the network.

Follow-ups
----------
- "Patch where it is looked up, not where it is defined": ``fetch_temperature`` uses the name
  ``urlopen`` imported into *this* module, so that is the name to replace.
- Why ``spec``/``autospec``? A bare Mock accepts any attribute, so a typo like
  ``notifier.sned(...)`` silently "works" in tests.
"""
from __future__ import annotations

import json
import sys
from collections.abc import Callable
from typing import Protocol
from unittest import mock
from unittest.mock import MagicMock, Mock, call
from urllib.parse import quote
from urllib.request import urlopen

import pytest


class Notifier(Protocol):
    def send(self, to: str, message: str) -> None: ...


class EmailNotifier:
    """The production notifier (would talk to SMTP). Tests never use it directly."""

    def send(self, to: str, message: str) -> None:  # pragma: no cover - real side effect
        raise RuntimeError("no SMTP server in this environment")


def fetch_temperature(city: str, base_url: str = "https://weather.example.com") -> float:
    with urlopen(f"{base_url}/current?city={quote(city)}", timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return float(payload["temp_c"])


def check_heat_alerts(
    cities: list[str],
    get_temp: Callable[[str], float],
    notifier: Notifier,
    threshold: float = 35.0,
    recipient: str = "oncall@example.com",
) -> list[str]:
    alerts: list[str] = []
    for city in cities:
        try:
            temp = get_temp(city)
        except ConnectionError:
            alerts.append(f"{city}: unavailable")
            continue
        if temp >= threshold:
            notifier.send(recipient, f"Heat alert: {city} at {temp:.1f}C")
            alerts.append(city)
    return alerts


def solve(cities: list[str], temps: dict[str, float], threshold: float = 35.0) -> list[str]:
    return check_heat_alerts(cities, temps.__getitem__, Mock(spec=EmailNotifier), threshold)


# ------------------------------------------------------------------ embedded pytest suite
@pytest.fixture
def notifier():
    return Mock(spec=EmailNotifier)  # spec: only real attributes exist


def test_alert_sent_only_for_hot_cities(notifier):
    temps = {"Pune": 38.0, "Oslo": 9.0, "Dubai": 35.0}
    result = check_heat_alerts(["Pune", "Oslo", "Dubai"], temps.__getitem__, notifier, 35.0)
    assert result == ["Pune", "Dubai"]
    assert notifier.send.call_args_list == [
        call("oncall@example.com", "Heat alert: Pune at 38.0C"),
        call("oncall@example.com", "Heat alert: Dubai at 35.0C"),
    ]


def test_outage_is_reported_and_job_continues(notifier):
    get_temp = Mock(side_effect=[ConnectionError("timeout"), 40.0])  # one result per call
    result = check_heat_alerts(["Lima", "Cairo"], get_temp, notifier)
    assert result == ["Lima: unavailable", "Cairo"]
    assert get_temp.call_count == 2
    notifier.send.assert_called_once_with("oncall@example.com", "Heat alert: Cairo at 40.0C")


def test_no_alerts_means_no_notifications(notifier):
    check_heat_alerts(["Oslo"], lambda c: 3.0, notifier)
    notifier.send.assert_not_called()


def test_spec_catches_typos(notifier):
    with pytest.raises(AttributeError):
        notifier.sned("x", "y")  # a bare Mock() would accept this silently


def test_autospec_checks_call_signature():
    fake_send = mock.create_autospec(EmailNotifier().send)
    with pytest.raises(TypeError):
        fake_send("only-one-argument")


def _fake_response(body: bytes) -> MagicMock:
    response = MagicMock()
    response.read.return_value = body
    response.__enter__.return_value = response  # support "with urlopen(...) as response"
    return response


def test_fetch_temperature_patches_urlopen_where_used():
    this_module = sys.modules[__name__]
    with mock.patch.object(this_module, "urlopen",
                           return_value=_fake_response(b'{"temp_c": 31.5}')) as fake:
        assert fetch_temperature("New York", "https://w.test") == 31.5
    fake.assert_called_once_with("https://w.test/current?city=New%20York", timeout=5)


def test_fetch_temperature_propagates_network_errors():
    this_module = sys.modules[__name__]
    with mock.patch.object(this_module, "urlopen", side_effect=ConnectionError("down")):
        with pytest.raises(ConnectionError):
            fetch_temperature("Oslo")


def main() -> None:
    notifier = Mock(spec=EmailNotifier)
    temps = {"Pune": 38.0, "Oslo": 9.0}
    print("alerts:", check_heat_alerts(["Pune", "Oslo"], temps.get, notifier, 35.0))
    print("notifier.send calls:", notifier.send.call_args_list)

    flaky = Mock(side_effect=[ConnectionError("timeout"), 41.2])
    print("with an outage:", check_heat_alerts(["Lima", "Cairo"], flaky, notifier))
    print("get_temp was called with:", flaky.call_args_list)

    loose = Mock()
    loose.sned("typo goes unnoticed")
    print("bare Mock accepted a typo; recorded calls:", loose.mock_calls)

    this_module = sys.modules[__name__]
    with mock.patch.object(this_module, "urlopen",
                           return_value=_fake_response(b'{"temp_c": 27.25}')) as fake:
        print("fetch_temperature with patched urlopen:", fetch_temperature("Rio"))
        print("urlopen called with:", fake.call_args)
    print()
    from ch31_testkit import print_results, run_embedded_tests

    print_results(run_embedded_tests(__file__))


if __name__ == "__main__":
    main()
