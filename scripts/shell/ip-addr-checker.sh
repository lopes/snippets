#!/usr/bin/env bash

# In SOC, when an external IP address is involved in an incident,
# we check it to try to identify the owner and if there is any
# incident related to that address. A few sites in internet
# offer this service, such as AbuseIPDB (https://www.abuseipdb.com/),
# Greynoise (https://www.greynoise.io/), and
# VirusTotal (https://www.virustotal.com/).
#
# Author.: Joe Lopes <lopes.id>
# Date...: 2022-09-02
# License: MIT
##


ABUSEIPDB_KEY="$APIKEY_ABUSEIPDB"
GREYNOISE_KEY="$APIKEY_GREYNOISE"
VIRUSTOTAL_KEY="$APIKEY_VIRUSTOTAL"
IPADDRESS=0


function argparse() {
  # Parses CLI arguments filling the required variables
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --abuseipdb-key|-a)
        ABUSEIPDB_KEY="$2"
        shift 2
        ;;
      --greynoise-key|-g)
        GREYNOISE_KEY="$2"
        shift 2
        ;;
      --virustotal-key|-v)
        VIRUSTOTAL_KEY="$2"
        shift 2
        ;;
      --help|-h)
        help
        exit 0
        ;;
      -*)
        echo "Unknown option $1"
        exit 1
        ;;
      *)
        IPADDRESS="$1"
        shift
        ;;
    esac
  done
}

function help() {
  echo "
This script fetches data on these 3 sites (in the future we can
add more) and bring it to the engineer. Data include any
evaluation of that IP address (like poor, good, neutral), the
ISP responsible for the address, and the geolocation -if available.
This script will get the API keys in environment variables and
through arguments. If an API key is informed in both ways, the
CLI argument will overwrite the other, thus it has more priority.


Usage:
  checkip [options] <ip-address>

Options:
  --abuseipdb-key KEY  : API key for api.abuseipdb.com default: \$APIKEY_ABUSEIPDB
  --greynoise-key KEY  : API key for api.greynoise.io  default: \$APIKEY_GREYNOISE
  --virustotal-key KEY : API key for virustotal.com    default: \$APIKEY_VIRUSTOTAL

Examples:
  checkip 8.8.8.8
  checkip --abuseipdb-key MYS3CRETAPIKEY 8.8.8.8
  checkip --greynoise-key S3CRETAPIKEY 8.8.8.8
  checkip --abuseipdb-key MYS3CRETAPIKEY --greynoise-key S3CRETAPIKEY 8.8.8.8
"
}

function request() {
  # Make an HTTP request to retrieve data from services.
  local -r srv=$1
  local -r ipa=$2
  local -r key=$3

  case "${srv}" in
    abuseipdb)
      local -r url="https://api.abuseipdb.com/api/v2/check"
      curl -sG \
        --url "${url}" \
        --data-urlencode "ipAddress=${ipa}" \
        --data maxAgeInDays=90 \
        --data verbose \
        --header "Key: ${key}" \
        --header "Accept: application/json" | tr -d '\n' | tr -s ' '
    ;;
    greynoise)
      local -r url="https://api.greynoise.io/v3/community"
      curl -sG \
        --url "${url}/${ipa}" \
        --header "Accept: application/json" \
        --header "key: ${key}" | tr -d '\n' | tr -s ' '
    ;;
    virustotal)
      local -r url="https://www.virustotal.com/api/v3/ip_addresses"
      curl -sG \
        --url "${url}/${ipa}" \
        --header "Accept: application/json" \
        --header "X-Apikey: ${key}"  | tr -d '\n' | tr -s ' '
  esac
}

function abuseipdb() {
  # Queries abuseipdb.com for information on an IP address
  local -r ipaddress=$1
  local -r abuseipdb_key=$2

  local -r data=$(request "abuseipdb" "${ipaddress}" "${abuseipdb_key}")
  local -r confidence_score=$(echo "${data}" | sed -n 's/.*\"abuseConfidenceScore\":\([0-9]*\).*/\1/p')
  local -r domain=$(echo "${data}" | sed -n 's/.*\"domain\":\"\([^"]*\)\".*/\1/p')
  local -r numofreports=$(echo "${data}" | sed -n 's/.*\"totalReports\":\([0-9]*\).*/\1/p')
  local -r allowlisted=$(echo "${data}" | sed -n 's/.*\"isWhitelisted\":\([^,]*\).*/\1/p')
  local -r countrycode=$(echo "${data}" | sed -n 's/.*\"countryCode\":\"\([^"]*\)\".*/\1/p')
  local -r isp=$(echo "${data}" | sed -n 's/.*\"isp\":\"\([^"]*\)\".*/\1/p')

  echo "${ipaddress} @ AbuseIPDB
Confidence score..........: ${confidence_score}
Domain....................: ${domain}
Number of reports.........: ${numofreports}
Allow listed..............? ${allowlisted}
Country code..............: ${countrycode}
ISP.......................: ${isp}
"
}

function greynoise() {
  # Queries greynoise.io for information on an IP address
  local -r ipaddress=$1
  local -r greynoise_key=$2

  local -r data=$(request "greynoise" "${ipaddress}" "${greynoise_key}")
  local -r classification=$(echo "${data}" | sed -n 's/.*\"classification\": \"\([^"]*\)\".*/\1/p')
  local -r noise=$(echo "${data}" | sed -n 's/.*\"noise\": \([^,]*\).*/\1/p')
  local -r riot=$(echo "${data}" | sed -n 's/.*\"riot\": \([^,]*\).*/\1/p')
  local -r name=$(echo "${data}" | sed -n 's/.*\"name\": \"\([^"]*\)\".*/\1/p')

  echo "${ipaddress} @ GreyNoise
Classification............: ${classification}
Noise.....................? ${noise}
Riot......................? ${riot}
Name......................: ${name}
"
}

function virustotal() {
  # Queries virustotal.com for information on an IP address
  local -r ipaddress=$1
  local -r virustotal_key=$2

  local -r data=$(request "virustotal" "${ipaddress}" "${virustotal_key}")
  local -r rir=$(echo "${data}" | sed -n 's/.*\"regional_internet_registry\": \"\([^"]*\)\".*/\1/p')
  local -r net=$(echo "${data}" | sed -n 's/.*\"network\": \"\([^"]*\)\".*/\1/p')
  local -r asn=$(echo "${data}" | sed -n 's/.*\"asn\": \([0-9]*\).*/\1/p')
  local -r owner=$(echo "${data}" | sed -n 's/.*\"as_owner\": \"\([^"]*\)\".*/\1/p')
  local -r country=$(echo "${data}" | sed -n 's/.*\"country\": \"\([^"]*\)\".*/\1/p')
  # unfortunatelly, sed does not support non-greedy regexes (? operator)
  local -r stats=$(echo "${data}" | sed -n 's/.*\(\"last_analysis_stats\": { \(\"[a-z]*\": [0-9]*, \)\{4\}"[a-z]*\": [0-9]* }\).*/\1/gp')
  local -r stats_harmless=$(echo "${stats}" | sed -n 's/.*\"harmless\": \([0-9]*\).*/\1/p')
  local -r stats_malicious=$(echo "${stats}" | sed -n 's/.*\"malicious\": \([0-9]*\).*/\1/p')
  local -r stats_suspicious=$(echo "${stats}" | sed -n 's/.*\"suspicious\": \([0-9]*\).*/\1/p')
  local -r stats_undetected=$(echo "${stats}" | sed -n 's/.*\"undetected\": \([0-9]*\).*/\1/p')
  local -r stats_timeout=$(echo "${stats}" | sed -n 's/.*\"timeout\": \([0-9]*\).*/\1/p')

  echo "${ipaddress} @ VirusTotal
Regional Internet Registry: ${rir}
Network...................: ${net}
ASN.......................: ${asn}
Owner.....................: ${owner}
Country...................: ${country}
Last analysis stats
  Harmless................: ${stats_harmless}
  Malicious...............: ${stats_malicious}
  Suspicious..............: ${stats_suspicious}
  Undetected..............: ${stats_undetected}
  Timeout.................: ${stats_timeout}
"
}


argparse "$@"
checked_ip="false"

if [[ -n ${ABUSEIPDB_KEY} ]]; then
  abuseipdb "${IPADDRESS}" "${ABUSEIPDB_KEY}"
  checked_ip="true"
fi
if [[ -n ${GREYNOISE_KEY} ]]; then
  greynoise "${IPADDRESS}" "${GREYNOISE_KEY}"
  checked_ip="true"
fi
if [[ -n ${VIRUSTOTAL_KEY} ]]; then
  virustotal "${IPADDRESS}" "${VIRUSTOTAL_KEY}"
  checked_ip="true"
fi

if ! ${checked_ip}; then
  echo "\
Error: Could not find any API key.
You must set at least one API key through environment variable or CLI argument.
See the help (-h) for more details.
"
  exit 1
fi
