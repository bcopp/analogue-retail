variable "project_id" {
  description = "The GCP project ID"
  type        = string
  default     = "boost-446418"
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "bucket_name" {
  description = "The name of the GCS bucket"
  type        = string
  default     = "boost-446418-dev-products"
} 