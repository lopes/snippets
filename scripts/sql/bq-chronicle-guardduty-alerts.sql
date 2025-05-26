SELECT
  `metadata`.product_event_type,
  `security_result`[SAFE_OFFSET(0)].severity as severity,
  COUNT(`metadata`.product_event_type) as event_count
FROM `chronicle-nubank.datalake.events`
WHERE
  `metadata`.log_type = "GUARDDUTY"
GROUP BY `metadata`.product_event_type, severity
ORDER BY event_count DESC
LIMIT 1000
