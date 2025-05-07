output "cluster_name" {
  description = "The name of the GKE cluster"
  value       = module.cluster.cluster_name
}

output "cluster_endpoint" {
  description = "The IP address of the cluster endpoint"
  value       = module.cluster.cluster_endpoint
}

output "ingress_ip" {
  description = "The IP address of the ingress controller"
  value       = module.cluster.ingress_ip
}

output "name_servers" {
  description = "The name servers for the DNS zone"
  value       = module.dns.name_servers
}

output "dns_name" {
  description = "The DNS name of the zone"
  value       = module.dns.dns_name
} 