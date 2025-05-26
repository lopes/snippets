SELECT
  log_type,
  SUM(normalized_event_count) AS snec,
  SUM(parsing_error_count)    AS spec,
  SUM(validation_error_count) AS svec,
  SUM(enrichment_error_count) AS seec
FROM `chronicle-nubank.datalake.ingestion_stats`
WHERE
  (
    TIMESTAMP_SECONDS(timestamp_sec) > TIMESTAMP("2023-11-29T14:00:00") and
    TIMESTAMP_SECONDS(timestamp_sec) < TIMESTAMP("2024-12-29T14:00:00")
  )
  -- (
  --   TIMESTAMP_TRUNC(_PARTITIONTIME, HOUR) > TIMESTAMP("2023-11-29T14:00:00") and
  --   TIMESTAMP_TRUNC(_PARTITIONTIME, HOUR) < TIMESTAMP("2023-12-06T14:00:00")
  -- )
GROUP BY log_type
ORDER BY spec DESC
LIMIT 1000
