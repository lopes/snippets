# Product: MISP Threat Intelligence
# Category: Information Security
# Supported Format: JSON
# Reference: https://medium.com/@thatsiemguy/how-to-integrate-misp-and-chronicle-siem-9e5fe5fde97c
# Last Updated: 2024-06-01

filter {
    ##
    # BASIC VARIABLES ASSERTION AND FIELDS EXTRACTION
    #
    mutate {
        replace => {
            "misp_url" => "misp.local"
            "threat_det" => ""
            "Attribute.id" => ""
            "Attribute.uuid" => ""
            "Attribute.type" => ""
            "Attribute.category" => ""
            "Attribute.comment" => ""
            "Attribute.timestamp" => ""
            "Attribute.first_seen" => ""
            "Attribute.last_seen" => ""
            "Attribute.Event.uuid" => ""
            "Attribute.Event.info" => ""
            "Attribute.Event.Orgc.name" => ""
            "Attribute.Event.threat_level_id" => ""
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
                "event.idm.entity.metadata.vendor_name" => "Circl"
                "event.idm.entity.metadata.product_name" => "MISP"
                "event.idm.entity.metadata.product_entity_id" => "%{Attribute.uuid}"
                "event.idm.entity.metadata.description" => "%{Attribute.Event.info}"
            }
        }


        ##
        # THREAT DATA
        #
        if [Attribute][id] != "" {
            mutate {
                replace => {
                    "threat_det.url_back_to_product" => "https://%{misp_url}/events/view/%{Attribute.event_id}"
                }
            }
        }

        if [Attribute][Event][Orgc][name] != "" {
            mutate {
                replace => {
                    "threat_det.threat_feed_name" => "%{Attribute.Event.Orgc.name}"
                }
            }
        }

        if [Attribute][type] != "" {
            mutate {
                merge => {
                    "threat_det.category_details" => "Attribute.type"
                }
            }
        }

        # severity: 1:High, 2:Medium, 3:Low, 4:Undefined
        if [Attribute][Event][threat_level_id] != "" {
            mutate {
                replace => {
                    "threat_det.severity_details" => "%{Attribute.Event.threat_level_id}"
                }
            }
            if [Attribute][Event][threat_level_id] == "1" {
                mutate {
                    replace => {
                        "threat_det.severity" => "HIGH"
                    }
                }
            } else if [Attribute][Event][threat_level_id] == "2" {
                mutate {
                    replace => {
                        "threat_det.severity" => "MEDIUM"
                    }
                }
            } else if [Attribute][Event][threat_level_id] == "3" {
                mutate {
                    replace => {
                        "threat_det.severity" => "LOW"
                    }
                }
            } else {
                mutate {
                    replace => {
                        "threat_det.severity" => "UNKNOWN_SEVERITY"
                    }
                }
            }
        }

        if [Attribute][Event][uuid] != "" {
            mutate {
                replace => {
                    "threat_det.threat_id" => "%{Attribute.Event.uuid}"
                }
            }
        }

        if [Attribute][category] != "" {
            mutate {
                merge => {
                    "threat_det.category_details" => "Attribute.category"
                }
            }
        }

        for index,tag in Attribute.Event.Tag {
            mutate {
                merge => {
                    "threat_det.category_details" => "tag.name"
                }
            }
        }

        if [threat_det] != "" {
            mutate {
                merge => {
                    "event.idm.entity.metadata.threat" => "threat_det"
                }
            }
        }
        else {
            drop {
                tag => "TAG_MALFORMED_MESSAGE"
            }
        }


        ##
        # IOCS
        #
        if ([Attribute][type] == "ip-dst" or [Attribute][type] == "ip-src") and [Attribute][value] != "" {
            mutate {
                replace => {
                    "event.idm.entity.metadata.entity_type" => "IP_ADDRESS"
                }
                merge => {
                    "event.idm.entity.entity.ip" => "Attribute.value"
                }
            }
        }

        if [Attribute][type] == "domain" and [Attribute][value] != "" {
            mutate {
                replace => {
                    "event.idm.entity.metadata.entity_type" => "DOMAIN_NAME"
                    "event.idm.entity.entity.hostname" => "%{Attribute.value}"
                }
            }
        }

        if [Attribute][type] == "sha256" and [Attribute][value] != "" {
            mutate {
                replace => {
                    "event.idm.entity.metadata.entity_type" => "FILE"
                    "event.idm.entity.entity.file.sha256" => "%{Attribute.value}"
                }
            }
        }
        if [Attribute][type] == "sha1" and [Attribute][value] != "" {
            mutate {
                replace => {
                    "event.idm.entity.metadata.entity_type" => "FILE"
                    "event.idm.entity.entity.file.sha1" => "%{Attribute.value}"
                }
            }
        }
        if [Attribute][type] == "md5" and [Attribute][value] != "" {
            mutate {
                replace => {
                    "event.idm.entity.metadata.entity_type" => "FILE"
                    "event.idm.entity.entity.file.md5" => "%{Attribute.value}"
                }
            }
        }


        ##
        # TIMESTAMPS
        #
        if [Attribute][timestamp] != "" {
            date {
                match => ["Attribute.timestamp", "UNIX"]
                target => "event.idm.entity.metadata.interval.start_time"
            }
        }

        if [Attribute][first_seen] != "" {
            # gsub truncates the seconds to match the date plugin requisites
            mutate {
                gsub => [
                    "Attribute.first_seen", "(.{23})...(.{6})", "$1$2"
                ]
            }
            date {
                match => ["Attribute.first_seen", "yyyy-MM-ddTHH:mm:ss.SSSZZ"]
                target => "event.idm.entity.metadata.interval.start_time"
            }
        }

        if [Attribute][last_seen] != "" {
            # gsub truncates the seconds to match the date plugin requisites
            mutate {
                gsub => [
                    "Attribute.last_seen", "(.{23})...(.{6})", "$1$2"
                ]
            }
            date {
                match => ["Attribute.last_seen", "yyyy-MM-ddTHH:mm:ss.SSSZZ"]
                target => "event.idm.entity.metadata.interval.end_time"
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
