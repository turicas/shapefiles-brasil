import argparse
import json
from unicodedata import normalize

import fiona
import topojson as tp


def normalize_text(text):
    return normalize("NFKD", text).encode("ascii", errors="ignore").decode("ascii").lower().strip()


UF_SIGLA = {
    "Acre": "AC",
    "Alagoas": "AL",
    "Amapá": "AP",
    "Amazonas": "AM",
    "Bahia": "BA",
    "Ceará": "CE",
    "Distrito Federal": "DF",
    "Espírito Santo": "ES",
    "Goiás": "GO",
    "Maranhão": "MA",
    "Mato Grosso do Sul": "MS",
    "Mato Grosso": "MT",
    "Minas Gerais": "MG",
    "Pará": "PA",
    "Paraíba": "PB",
    "Paraná": "PR",
    "Pernambuco": "PE",
    "Piauí": "PI",
    "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS",
    "Rondônia": "RO",
    "Roraima": "RR",
    "Santa Catarina": "SC",
    "São Paulo": "SP",
    "Sergipe": "SE",
    "Tocantins": "TO",
}
UF_NOME_NORMALIZADO = {normalize_text(key): key for key in UF_SIGLA.keys()}


def round_coordinates(coords, precision=5):
    if isinstance(coords[0], (int, float)):
        return [round(c, precision) for c in coords]
    else:
        return [round_coordinates(c, precision) for c in coords]


def converte_propriedades(props: dict):
    if "NM_MUNICIP" in props:
        props["nome"] = props.pop("NM_MUNICIP")
        props["codigo"] = props.pop("CD_GEOCMU")
    elif "NM_ESTADO" in props:
        nome = props.pop("NM_ESTADO")
        nome_normalizado = normalize_text(nome)
        props["nome"] = UF_NOME_NORMALIZADO[nome_normalizado]
        props["sigla"] = UF_SIGLA[props["nome"]]
        props["codigo"] = props.pop("CD_GEOCUF")
        props["regiao"] = props.pop("NM_REGIAO").title()
    else:
        raise ValueError(f"Tipo de registro desconhecido - propriedades: {props}")
    expected_keys = {"nome", "codigo", "regiao", "sigla"}
    actual_keys = set(props.keys())
    diff = actual_keys - expected_keys
    if diff:
        raise ValueError(f"Chaves de propriedades desconhecidas: {', '.join(sorted(diff))}")
    return props


def convert_shp_to_geojson(input_filename, output_filename, simplify=False, tolerance=None, precision=5):
    input_filename = str(input_filename)
    if input_filename.lower().endswith(".zip") and not input_filename.lower().startswith("zip://"):
        input_filename = f"zip://{input_filename}"

    with fiona.open(input_filename) as shape_data:
        geojson = {"type": "FeatureCollection", "features": []}
        for item in shape_data:
            props = dict(item.properties)
            converte_propriedades(props)
            geometry = dict(item.geometry)
            geometry["coordinates"] = round_coordinates(geometry["coordinates"], precision)
            item_dict = {
                "type": "Feature",
                "id": item.id,
                "geometry": geometry,
                "properties": props,
            }
            geojson["features"].append(item_dict)

    if simplify and tolerance is not None:
        topo = tp.Topology(geojson, prequantize=False)
        area_tolerance = tolerance * tolerance * 0.5  # The tolerance for topojson is different - it's the minimum area
        topo = topo.toposimplify(epsilon=area_tolerance, simplify_algorithm="vw", simplify_with="simplification")
        geojson_str = topo.to_geojson()
        geojson = json.loads(geojson_str)
        for feature in geojson["features"]:
            feature["geometry"]["coordinates"] = round_coordinates(feature["geometry"]["coordinates"], precision)

    with open(output_filename, mode="w") as fobj:
        for chunk in json.JSONEncoder(separators=(",", ":")).iterencode(geojson):
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
    parser.add_argument(
        "--precision",
        type=int,
        default=5,
        help="Number of decimal places for coordinates (default: 5)",
    )
    parser.add_argument("input_filename", help="SHP file - can be a ZIP file (use: zip://filename.zip)")
    parser.add_argument("output_filename", help="GeoJSON filename")
    args = parser.parse_args()

    convert_shp_to_geojson(
        args.input_filename,
        args.output_filename,
        simplify=args.simplify,
        tolerance=args.tolerance,
        precision=args.precision,
    )


if __name__ == "__main__":
    main()
