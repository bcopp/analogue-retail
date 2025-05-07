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

# Enable Container Registry API
resource "google_project_service" "container_registry" {
  service = "containerregistry.googleapis.com"
  disable_on_destroy = false
}

# Create the artifacts bucket
resource "google_storage_bucket" "artifacts" {
  name          = "${var.project_id}-artifacts"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

# Get the GCR member from Secret Manager
data "google_secret_manager_secret_version" "gcr_member" {
  secret = "gcr-member"
}

# Container Registry IAM
resource "google_storage_bucket_iam_member" "viewer" {
  bucket = google_storage_bucket.artifacts.name
  role   = "roles/storage.objectViewer"
  member = "user:${data.google_secret_manager_secret_version.gcr_member.secret_data}"
}

resource "google_storage_bucket_iam_member" "writer" {
  bucket = google_storage_bucket.artifacts.name
  role   = "roles/storage.objectCreator"
  member = "user:${data.google_secret_manager_secret_version.gcr_member.secret_data}"
} 