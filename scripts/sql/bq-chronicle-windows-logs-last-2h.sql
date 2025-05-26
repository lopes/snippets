SELECT
  TIMESTAMP_SECONDS(`metadata`.event_timestamp.seconds) as ts,
  principal.ip,
  `metadata`.product_event_type
FROM `chronicle-nubank.datalake.events`
WHERE
  (
    `metadata`.log_type = "WINEVTLOG" or
    `metadata`.log_type = "WINDOWS_SYSMON"
  ) and
  TIMESTAMP_SECONDS(`metadata`.event_timestamp.seconds) >
  TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 HOUR)
ORDER BY ts ASC
LIMIT 1000
