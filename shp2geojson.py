import argparse
import json

import fiona
import topojson as tp


def convert_shp_to_geojson(input_filename, output_filename, simplify=False, tolerance=None):
    input_filename = str(input_filename)
    if input_filename.lower().endswith(".zip") and not input_filename.lower().startswith("zip://"):
        input_filename = f"zip://{input_filename}"

    with fiona.open(input_filename) as shape_data:
        geojson = {"type": "FeatureCollection", "features": []}
        for item in shape_data:
            item_dict = {
                "type": "Feature",
                "id": item.id,
                "geometry": dict(item.geometry),
                "properties": dict(item.properties),
            }
            geojson["features"].append(item_dict)

    if simplify and tolerance is not None:
        topo = tp.Topology(geojson, prequantize=False)
        area_tolerance = tolerance * tolerance * 0.5  # The tolerance for topojson is different - it's the minimum area
        topo = topo.toposimplify(epsilon=area_tolerance, simplify_algorithm="vw", simplify_with="simplification")
        geojson_str = topo.to_geojson()
        geojson = json.loads(geojson_str)

    with open(output_filename, mode="w") as fobj:
        for chunk in json.JSONEncoder().iterencode(geojson):
            fobj.write(chunk)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--simplify", action="store_true", help="Should simplify geometry?")
    parser.add_argument(
        "--tolerance",
        type=float,
        default=None,
        help="Tolerance to be used in simplify process",
    )
    parser.add_argument("input_filename", help="SHP file - can be a ZIP file (use: zip://filename.zip)")
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
