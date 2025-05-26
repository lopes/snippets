# Product: Hashcast
# Category: Information Security
# Supported Format: JSON
# Reference: https://lopes.id/2024-misp-chronicle-integration/
# Last Updated: 2025-04-25
#
# EXPECTED INPUT EXAMPLE:
# {
#   "email": "user@domain",
#   "password-type": "PLAIN",
#   "first-seen": "2024-12-31T14:52:11.122Z",
#   "password-value": "myleakedpass",
#   "detected-at": "2024-12-31T14:59:30.76Z",
#   "sources": "BIG_LEAKS",
#   "status": "ACTIVE"
# }
##

filter {
  ##
  # BASIC VARIABLES ASSERTION AND FIELDS EXTRACTION
  #
  mutate {
    replace => {
      "security_result" => ""
      "first-seen"      => ""
      "detected-at"     => ""
      "status"          => ""
    }
  }

  json {
    source         => "message"
    array_function => "split_columns"
    on_error       => "_not_json"
  }

  if [_not_json] {
    drop {
      tag => "TAG_MALFORMED_MESSAGE"
    }
  }
  else {
    mutate {
      replace => {
        "security_result.severity" => "HIGH"
        "security_result.summary" => "Leaked credential reported by: %{sources}"
        "security_result.description" => "Password: %{password-value}. Type:%{password-type}"
        "event.idm.read_only_udm.metadata.event_type" => "GENERIC_EVENT",
        "event.idm.read_only_udm.metadata.product_event_type" => "Leaked credential",
        "event.idm.read_only_udm.metadata.description" => "User %{email} has a leaked credential detected by Hashcast",
        "event.idm.read_only_udm.metadata.product_name" => "Hashcast",
        "event.idm.read_only_udm.metadata.vendor_name" => "Axur",
        "event.idm.read_only_udm.principal.email" => "%{email}",
        "event.idm.read_only_udm.principal.user.user_authentication_status" => "UNKNOWN_AUTHENTICATION_STATUS"
      }
    }

    # user status
    if [status] != "" {
        if [status] == "DEPROVISIONED" {
            mutate {
                replace => {
                    "event.idm.read_only_udm.principal.user.user_authentication_status" => "SUSPENDED"
                }
            }
        } else {
            mutate {
                replace => {
                    "event.idm.read_only_udm.principal.user.user_authentication_status" => "ACTIVE"
                }
            }
        }
    }

    # security_result
    mutate {
      merge => {
        "event.idm.read_only_udm.security_result" => "security_result"
      }
    }


    ##
    # TIMESTAMPS
    #
    if [first-seen] != "" {
      date {
        match => ["first-seen", "ISO8601", "yyyy-MM-ddTHH:mm:ss"]
        target => "event.idm.read_only_udm.metadata.collected_timestamp"
        timezone => "UTC"
      }
    }

    if [detected-at] != "" {
      date {
        match => ["detected-at", "ISO8601", "yyyy-MM-ddTHH:mm:ss"]
        target => "event.idm.read_only_udm.metadata.event_timestamp"
        timezone => "UTC"
      }
    }
  }


  ##
  # WRITING EVERYTHING BEFORE FINISH
  #
  # statedump{ label => "pre-output merge" }  # tshoot, comment on final version
  mutate {
    merge => {
      "@output" => "event"
    }
  }
}
