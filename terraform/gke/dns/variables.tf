variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "ingress_ip" {
  description = "The IP address of the ingress controller"
  type        = string
} 