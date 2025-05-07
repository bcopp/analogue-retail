terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Create DNS zone
resource "google_dns_managed_zone" "brendancopp" {
  name        = "brendancopp"
  dns_name    = "brendancopp.com."
  description = "DNS zone for brendancopp.com"
}

# Create DNS record
resource "google_dns_record_set" "www" {
  name         = "www.${google_dns_managed_zone.brendancopp.dns_name}"
  managed_zone = google_dns_managed_zone.brendancopp.name
  type         = "A"
  ttl          = 300

  rrdatas = [var.ingress_ip]
}

# Create DNS record for root domain
resource "google_dns_record_set" "root" {
  name         = google_dns_managed_zone.brendancopp.dns_name
  managed_zone = google_dns_managed_zone.brendancopp.name
  type         = "A"
  ttl          = 300

  rrdatas = [var.ingress_ip]
}

# Enable Cloud Domains API
resource "google_project_service" "domains" {
  service = "domains.googleapis.com"
  disable_on_destroy = false
}
