#!/bin/bash

set -e
DOWNLOAD_PATH="data/download"
OUTPUT_PATH="data/output"
DATASET="shapefiles-brasil"
TOLERANCES="full 0.001 0.005 0.01 0.05 0.1 0.2"
STATES="AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO"
mkdir -p "$DOWNLOAD_PATH" "$OUTPUT_PATH"

function extract_shp() {
  zip_filename=$1; shift
  tolerance=$1; shift
  output=$1; shift

  CMD="python shp2geojson.py zip://$zip_filename"
  if [ "$tolerance" != "full" ]; then
    OPTS="--simplify --tolerance=$tolerance"
  else
    OPTS=""
  fi
  $CMD "$output" $OPTS
}

function download_extract_upload() {
  state=$1; shift
  url=$1; shift
  defaultTolerance=$1

  zip_filename="$DOWNLOAD_PATH/${state}.zip"
  wget -O "$zip_filename" -c -t 0 "$url"
  for tolerance in $TOLERANCES; do
    echo $state $tolerance
    mkdir -p $OUTPUT_PATH/$tolerance
    output="$OUTPUT_PATH/$tolerance/${state}.geojson"
    extract_shp "$zip_filename" "$tolerance" "$output"
    s3cmd put "$output" "s3://dataset/$DATASET/$tolerance/${state}.geojson"
    if [[ $tolerance = $defaultTolerance ]]; then
      s3cmd put "$output" "s3://dataset/$DATASET/${state}.geojson"
    fi
    if [ "$tolerance" = "full" ]; then
      output_path="$OUTPUT_PATH/$tolerance/${state}"
      time python extrai_subfetuare.py "$output" "$output_path"
      s3cmd put ${output_path}/* "s3://dataset/$DATASET/$tolerance/${state}/"
      rm -rf "$output_path"
    fi
    rm -rf "$output"
  done
  time s3cmd put "$zip_filename" s3://mirror/$DATASET/$(basename $zip_filename)
  rm -rf "$zip_filename"
}

state="BR-UF"
url="http://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2018/Brasil/BR/br_unidades_da_federacao.zip"
download_extract_upload "$state" "$url" "0.1"

for state in $STATES; do
  echo $state
  state_lower=$(echo $state | tr A-Z a-z)
  url="http://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2018/UFs/${state}/${state_lower}_municipios.zip"
  download_extract_upload "$state" "$url" "0.005"
done

state="BR-municipios"
url="http://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2018/Brasil/BR/br_municipios.zip"
download_extract_upload "$state" "$url" "0.01"
