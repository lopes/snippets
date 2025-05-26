## jq Recipes

Counts the number of items inside the array alerts within reply.
`jq '.reply.alerts | length' cortex-alerts.json`

Gets Tesouro Direto bonds and filters out only IPCA+ 2025 from them.
`curl -s <https://www.tesourodireto.com.br/json/br/com/b3/tesourodireto/service/api/treasurybondsinfo.json> | jq '.response.TrsrBdTradgList[] | select(.TrsrBd.nm | test("IPCA+.*2035"; "i"))'`

Filters only the Technique and Tactic from MITRE ATT&CK's mapping.
`jq '.techniques[] | .techniqueID, .tactic' guardduty-navigator.json`

From all Slack user groups, filters the ones that match the regex and amongst them, shows only name, description, and handle.
`jq '.usergroups[] | select(.handle | test(".*on-?call")) | .name, .description, .handle' slack-user-groups-20230116.json`

Figures start with [!...](...)
`find ./content -type f -name "*.md" -exec grep -l "^.\\[.*\\]\\(.*\\)" {} \\;`
