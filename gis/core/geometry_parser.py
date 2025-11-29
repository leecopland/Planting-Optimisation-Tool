def parse_point(lat: float, lon: float):
    """Return an EE Point geometry."""
    import ee

    if lat is None or lon is None:
        raise ValueError("lat and lon must not be None")

    return ee.Geometry.Point([lon, lat])


def parse_multipoint(coords: list[tuple[float, float]]):
    """Return an EE MultiPoint geometry."""
    import ee

    if not coords or not isinstance(coords, list):
        raise ValueError("coords must be a list of (lat, lon) tuples")

    ee_coords = []
    for lat, lon in coords:
        ee_coords.append([lon, lat])  # EE uses lon, lat

    return ee.Geometry.MultiPoint(ee_coords)


def parse_polygon(coords: list[list[tuple[float, float]]]):
    """
    Return an EE Polygon geometry.
    Expects:
        [ [ (lat, lon), (lat, lon), ... ] ]  # rings

    Outer ring must be closed (first == last).
    """
    import ee

    if not coords or not isinstance(coords, list):
        raise ValueError("coords must be a list of rings")

    ee_rings = []
    for ring in coords:
        ee_ring = [[lon, lat] for (lat, lon) in ring]
        ee_rings.append(ee_ring)

    return ee.Geometry.Polygon(ee_rings)
