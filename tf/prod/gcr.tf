# Enable Container Registry API
resource "google_project_service" "container_registry" {
  service = "containerregistry.googleapis.com"
  disable_on_destroy = false
}

# Create Container Registry repository
resource "google_artifact_registry_repository" "retail_backend" {
  location      = var.region
  repository_id = "retail"
  description   = "Docker repository for retail-backend service"
  format        = "DOCKER"

  docker_config {
    immutable_tags = true
  }
}

# Get the GCR member from Secret Manager
data "google_secret_manager_secret_version" "gcr_member" {
  secret = "gcr-member"
}

# Add IAM for retail-backend service account
resource "google_artifact_registry_repository_iam_member" "retail_backend_viewer" {
  location   = google_artifact_registry_repository.retail_backend.location
  repository = google_artifact_registry_repository.retail_backend.name
  role       = "roles/artifactregistry.reader"
  member     = "user:${data.google_secret_manager_secret_version.gcr_member.secret_data}"
}

resource "google_artifact_registry_repository_iam_member" "retail_backend_writer" {
  location   = google_artifact_registry_repository.retail_backend.location
  repository = google_artifact_registry_repository.retail_backend.name
  role       = "roles/artifactregistry.writer"
  member     = "user:${data.google_secret_manager_secret_version.gcr_member.secret_data}"
} 