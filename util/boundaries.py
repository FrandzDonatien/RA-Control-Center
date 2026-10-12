import json
from pathlib import Path

import requests


CACHE_FILE = Path(__file__).resolve().parent / "togo_adm0.geojson"
API_URL = "https://www.geoboundaries.org/api/current/gbOpen/TGO/ADM0/"


def _download_boundaries():
    """Télécharge les frontières administratives nationales du Togo."""
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    metadata = response.json()
    geojson_url = metadata["gjDownloadURL"]

    geojson_response = requests.get(geojson_url, timeout=30)
    geojson_response.raise_for_status()

    geojson = geojson_response.json()

    # Mettre en cache le GeoJSON pour les prochains lancements.
    CACHE_FILE.write_text(
        json.dumps(geojson, ensure_ascii=False),
        encoding="utf-8",
    )

    return geojson


def load_togo_outline():
    """
    Retourne le contour principal du Togo sous forme de tuples
    (longitude, latitude), compatibles avec le Canvas Tkinter.
    """
    if CACHE_FILE.exists():
        try:
            geojson = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            geojson = _download_boundaries()
    else:
        geojson = _download_boundaries()

    features = geojson.get("features", [])
    if not features:
        raise ValueError("Aucune frontière du Togo trouvée dans le GeoJSON.")

    geometry = features[0]["geometry"]
    geometry_type = geometry["type"]
    polygons = geometry["coordinates"]

    if geometry_type == "Polygon":
        coordinates = polygons[0]

    elif geometry_type == "MultiPolygon":
        # Conserver le polygone extérieur ayant la plus grande aire.
        def polygon_area(polygon):
            ring = polygon[0]
            return abs(sum(
                ring[i][0] * ring[i + 1][1]
                - ring[i + 1][0] * ring[i][1]
                for i in range(len(ring) - 1)
            ))

        coordinates = max(polygons, key=polygon_area)[0]

    else:
        raise ValueError(
            f"Type de géométrie non pris en charge : {geometry_type}"
        )

    return [
        (longitude, latitude)
        for longitude, latitude, *rest in coordinates
    ]


TOGO_OUTLINE = load_togo_outline()
