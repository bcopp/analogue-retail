terraform {
  backend "gcs" {
    bucket = "boost-446418-tf-remote"
    prefix = "gke/state"
  }
} 