#######################
# DNS
#######################

# Create DNS zone
resource "google_dns_managed_zone" "brendancopp" {
  name        = "brendancopp-com"
  dns_name    = "brendancopp.com."
  description = "DNS zone for domain: brendancopp.com"
  visibility  = "public"

  dnssec_config {
    state = "on"
    non_existence = "nsec3"
    default_key_specs {
      algorithm  = "rsasha256"
      key_length = 2048
      key_type   = "keySigning"
      kind       = "dns#dnsKeySpec"
    }
    default_key_specs {
      algorithm  = "rsasha256"
      key_length = 1024
      key_type   = "zoneSigning"
      kind       = "dns#dnsKeySpec"
    }
  }
}

# Create DNS record for CDN
resource "google_dns_record_set" "cdn" {
  name         = google_dns_managed_zone.brendancopp.dns_name
  managed_zone = google_dns_managed_zone.brendancopp.name
  type         = "A"
  ttl          = 300
  rrdatas      = [google_compute_global_address.website_ip.address]
}

# Create DNS record for www subdomain (CDN)
resource "google_dns_record_set" "www_cdn" {
  name         = "www.${google_dns_managed_zone.brendancopp.dns_name}"
  managed_zone = google_dns_managed_zone.brendancopp.name
  type         = "CNAME"
  ttl          = 300
  rrdatas      = [google_dns_managed_zone.brendancopp.dns_name]
}

# Create DNS record for GKE ingress
resource "google_dns_record_set" "gke" {
  name         = "api.${google_dns_managed_zone.brendancopp.dns_name}"
  managed_zone = google_dns_managed_zone.brendancopp.name
  type         = "A"
  ttl          = 300
  rrdatas      = [google_compute_global_address.ingress_ip.address]
}

# Enable Cloud Domains API
resource "google_project_service" "domains" {
  service = "domains.googleapis.com"
  disable_on_destroy = false
}