# Create the production GCS bucket
resource "google_storage_bucket" "prod_website" {
  name          = "brendancopp.com"
  location      = "US"
  force_destroy = true

  # Enable uniform bucket-level access
  uniform_bucket_level_access = true

  # Website configuration
  website {
    main_page_suffix = "index.html"
    not_found_page   = "index.html"
  }

  # Enable versioning
  versioning {
    enabled = true
  }

  # CORS configuration
  cors {
    origin          = ["https://brendancopp.com"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

# Make the bucket publicly readable
resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.prod_website.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# Create a backend bucket for the CDN
resource "google_compute_backend_bucket" "website_backend" {
  name        = "website-backend"
  bucket_name = google_storage_bucket.prod_website.name
  enable_cdn  = true
}

# Create a global IP address
resource "google_compute_global_address" "website_ip" {
  name = "website-ip"
}

# Create a URL map
resource "google_compute_url_map" "website_url_map" {
  name            = "website-url-map"
  default_service = google_compute_backend_bucket.website_backend.id

  host_rule {
    hosts        = ["brendancopp.com", "www.brendancopp.com"]
    path_matcher = "allpaths"
  }

  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_bucket.website_backend.id
  }
}

# Create an HTTPS proxy
resource "google_compute_target_https_proxy" "website_https_proxy" {
  name             = "website-https-proxy"
  url_map          = google_compute_url_map.website_url_map.id
  ssl_certificates = [google_compute_managed_ssl_certificate.website_cert.id]
}

# Create a managed SSL certificate
resource "google_compute_managed_ssl_certificate" "website_cert" {
  name = "website-cert"

  managed {
    domains = ["brendancopp.com", "www.brendancopp.com"]
  }
}

# Create a forwarding rule
resource "google_compute_global_forwarding_rule" "website_forwarding_rule" {
  name       = "website-forwarding-rule"
  target     = google_compute_target_https_proxy.website_https_proxy.id
  port_range = "443"
  ip_address = google_compute_global_address.website_ip.address
}

# Output the CDN IP for DNS configuration
output "cdn_ip" {
  value = google_compute_global_address.website_ip.address
} 