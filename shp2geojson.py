import argparse
import json

import fiona
from shapely.geometry import shape


def convert_shp_to_geojson(
    input_filename, output_filename, simplify=False, tolerance=None
):
    input_filename = str(input_filename)
    if input_filename.lower().endswith(".zip") and not input_filename.lower().startswith("zip://"):
        input_filename = f"zip://{input_filename}"
    shape_data = fiona.open(input_filename)
    geojson = {"type": "FeatureCollection", "features": []}
    for item in shape_data:
        if simplify:
            item["geometry"] = (
                shape(item["geometry"]).simplify(tolerance).__geo_interface__
            )
        geojson["features"].append(item)
    with open(output_filename, mode="w") as fobj:
        for chunk in json.JSONEncoder().iterencode(geojson):
            fobj.write(chunk)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--simplify", action="store_true", help="Should simplify geometry?"
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=None,
        help="Tolerance to be used in simplify process",
    )
    parser.add_argument(
        "input_filename", help="SHP file - can be a ZIP file (use: zip://filename.zip)"
    )
    parser.add_argument("output_filename", help="GeoJSON filename")
    args = parser.parse_args()

    convert_shp_to_geojson(
        args.input_filename,
        args.output_filename,
        simplify=args.simplify,
        tolerance=args.tolerance,
    )


if __name__ == "__main__":
    main()
