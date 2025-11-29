from unittest.mock import patch, MagicMock
import builtins

from core.gee_client import init_gee
from core.geometry_parser import parse_point, parse_multipoint, parse_polygon


# Helper to create fake ee module for mocking
def make_fake_ee():
    fake = MagicMock()
    fake.Geometry = MagicMock()
    fake.ServiceAccountCredentials = MagicMock()
    fake.Initialize = MagicMock()
    return fake


# init_gee test


@patch("core.gee_client.SERVICE_ACCOUNT", "sa@example.com")
@patch("core.gee_client.KEY_PATH", "/tmp/key.json")
def test_init_gee():
    fake_ee = make_fake_ee()

    # Patch import ee inside the function
    with patch.object(builtins, "__import__", return_value=fake_ee):
        result = init_gee()

    assert result is True
    fake_ee.ServiceAccountCredentials.assert_called_once_with(
        "sa@example.com", "/tmp/key.json"
    )
    fake_ee.Initialize.assert_called_once()


# parse_point test


def test_parse_point():
    fake_ee = make_fake_ee()

    with patch.object(builtins, "__import__", return_value=fake_ee):
        g = parse_point(-8.55, 125.57)

    fake_ee.Geometry.Point.assert_called_once_with([125.57, -8.55])
    assert g == fake_ee.Geometry.Point.return_value


# parse_multipoint test


def test_parse_multipoint():
    fake_ee = make_fake_ee()

    coords = [(-8.55, 125.57), (-8.56, 125.58)]

    with patch.object(builtins, "__import__", return_value=fake_ee):
        g = parse_multipoint(coords)

    fake_ee.Geometry.MultiPoint.assert_called_once_with(
        [[125.57, -8.55], [125.58, -8.56]]
    )
    assert g == fake_ee.Geometry.MultiPoint.return_value


# parse_polygon test


def test_parse_polygon():
    fake_ee = make_fake_ee()

    coords = [
        [
            (-8.55, 125.57),
            (-8.56, 125.57),
            (-8.56, 125.58),
            (-8.55, 125.58),
            (-8.55, 125.57),
        ]
    ]

    with patch.object(builtins, "__import__", return_value=fake_ee):
        g = parse_polygon(coords)

    fake_ee.Geometry.Polygon.assert_called_once_with(
        [
            [
                [125.57, -8.55],
                [125.57, -8.56],
                [125.58, -8.56],
                [125.58, -8.55],
                [125.57, -8.55],
            ]
        ]
    )
    assert g == fake_ee.Geometry.Polygon.return_value
