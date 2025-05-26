#!/bin/sh

# Retrieves alerts from Cortex XDR.
# PARAMETERS:
#   - $1: First item (start)
#   - $2: Number of items at each round (must be <= 100)
#   - $3: Number of pages desired (number of rounds)
# REQUIRES:
#   - API key and its ID from Cortex XDR
#   - Standard Authentication for the API key
# USAGE:
#   APIKEYID=88 APIKEY="my.looong.api.key.from.cortex" sh ${0} 0 100 20
# DATE: 2023-11-03
# AUTHOR: José Lopes <lopes.id>
# LICENSE: MIT
##


function get_alerts() {
  # Fetches alerts from Cortex XDR API
  # Set the URL with your FQDN!

  local from="$1"
  local to="$2"
  curl --silent --request POST \
    --url https://FQDN.paloaltonetworks.com/public_api/v1/alerts/get_alerts_multi_events \
    --header 'Accept: application/json' \
    --header 'Content-Type: application/json' \
    --header "x-xdr-auth-id: ${APIKEYID}" \
    --header "Authorization: ${APIKEY}" \
    --data '{
    "request_data": {
      "filters": [
        {
          "field": "severity",
          "operator": "in",
          "value": [
            "low",
            "medium"
          ]
        }
      ],
      "search_from": '"${from}"',
      "search_to": '"${to}"',
      "sort": {
        "field": "creation_time",
        "keyword": "desc"
      }
    }
  }'
}

function paginator() {
  # Paginates through chunks of alerts in Cortex XDR
  # NOTE: The total number of alerts come in the response under total_count
  # TODO: Understand if the response is inclusive or exclusive (last item)

  local start=$1
  local items=$2
  local pages=$3
  local end=$(( $start + $items ))
  local page=1
  local bname="cortex-alerts-$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

  while [ ${page} -le ${pages} ]; do
    local fname="${bname}-${page}.json"
    echo -n "[${page}/${pages}] "
    get_alerts "${start}" "${end}" > "${fname}"
    echo "Page ${page} (${start} to ${end}) stored in ${fname}"
    (( page++ ))
    (( start+=items ))
    (( end+=items ))
  done
}


paginator "$1" "$2" "$3"
