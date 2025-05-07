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

module "cluster" {
  source = "./cluster"

  project_id    = var.project_id
  region        = var.region
  cluster_name  = var.cluster_name
  subnet_cidr   = var.subnet_cidr
  pods_cidr     = var.pods_cidr
  services_cidr = var.services_cidr
  master_cidr   = var.master_cidr
}

module "dns" {
  source = "./dns"

  project_id  = var.project_id
  region      = var.region
  ingress_ip  = module.cluster.ingress_ip
} 