SELECT
  log_type as log_source,
  sum(log_count) as sum_log_count
FROM `chronicle-nubank.datalake.ingestion_metrics`
where
  log_type is not null
group by log_source
order by sum_log_count desc
