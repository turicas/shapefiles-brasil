import argparse
import json
from pathlib import Path

import rows
from tqdm import tqdm


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_geojson")
    parser.add_argument("output_path")
    args = parser.parse_args()
    input_geojson = Path(args.input_geojson)
    output_path = Path(args.output_path)
    if not output_path.exists():
        output_path.mkdir(parents=True)

    with open(input_geojson) as fobj:
        data = json.load(fobj)
    for feature in tqdm(data["features"]):
        name = feature["properties"]["NM_MUNICIP"]
        name_slug = rows.fields.slug(name, separator="-")
        filename = output_path / f"{name_slug}.geojson"
        with open(filename, mode="w") as fobj:
            json.dump(feature, fobj)
