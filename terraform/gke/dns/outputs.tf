output "name_servers" {
  description = "The name servers for the DNS zone"
  value       = google_dns_managed_zone.brendancopp.name_servers
}
 
output "dns_name" {
  description = "The DNS name of the zone"
  value       = google_dns_managed_zone.brendancopp.dns_name
} 