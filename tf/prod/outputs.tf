output "ingress_ip" {
  description = "The IP address of the ingress controller"
  value       = google_compute_global_address.ingress_ip.address
}

output "cluster_name" {
  description = "The name of the GKE cluster"
  value       = google_container_cluster.primary.name
}

output "cluster_endpoint" {
  description = "The IP address of the cluster endpoint"
  value       = google_container_cluster.primary.endpoint
}

output "artifact_registry_repository_name" {
  description = "The name of the artifact registry repository"
  value       = google_artifact_registry_repository.retail_backend.name
}