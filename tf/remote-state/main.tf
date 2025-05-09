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

# Enable Cloud Storage API
resource "google_project_service" "storage_api" {
  service = "storage.googleapis.com"
  disable_on_destroy = false
}

# Create the state bucket
resource "google_storage_bucket" "terraform_state" {
  name          = "${var.project_id}-tf-remote"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      num_newer_versions = 3
    }
    action {
      type = "Delete"
    }
  }
} 