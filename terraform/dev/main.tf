terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = "boost-446418"
  region  = "us-central1"
}

# Create the development GCS bucket
resource "google_storage_bucket" "dev_products" {
  name          = "boost-446418-dev-products"
  location      = "US"
  force_destroy = true

  # Enable uniform bucket-level access
  uniform_bucket_level_access = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

# Get the GCR member from Secret Manager
data "google_secret_manager_secret_version" "gcr_member" {
  secret = "gcr-member"
}

# Make the bucket publicly readable
resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.dev_products.name
  role   = "roles/storage.objectViewer"
  member = "user:${data.google_secret_manager_secret_version.gcr_member.secret_data}"
}
