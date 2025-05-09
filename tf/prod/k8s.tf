resource "kubernetes_namespace" "mysql" {
  metadata {
    name = "mysql"
  }
}

resource "kubernetes_namespace" "retail" {
  metadata {
    name = "retail"
  }
}

# Get the GCR member from Secret Manager
data "google_secret_manager_secret_version" "mysql_root_password" {
  secret = "analogue-mysql-password-root"
}

# MySQL Deployment
resource "kubernetes_deployment" "mysql" {
  metadata {
    name      = "mysql"
    namespace = kubernetes_namespace.mysql.metadata[0].name
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "mysql"
      }
    }

    template {
      metadata {
        labels = {
          app = "mysql"
        }
      }

      spec {
        security_context {
          fs_group = 999
        }

        container {
          image = "mysql:9.3.0"
          name  = "mysql"

          env {
            name  = "MYSQL_ROOT_PASSWORD"
            value = "${data.google_secret_manager_secret_version.mysql_root_password.secret_data}"
          }

          env {
            name  = "MYSQL_DATABASE"
            value = "retail"
          }

          port {
            container_port = 3306
          }

          resources {
            requests = {
              cpu    = "250m"
              memory = "1Gi"
            }
            limits = {
              cpu    = "500m"
              memory = "2Gi"
            }
          }

          liveness_probe {
            exec {
              command = ["mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${data.google_secret_manager_secret_version.mysql_root_password.secret_data}"]
            }
            initial_delay_seconds = 30
            period_seconds       = 10
            timeout_seconds      = 5
          }

          readiness_probe {
            exec {
              command = ["mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${data.google_secret_manager_secret_version.mysql_root_password.secret_data}"]
            }
            initial_delay_seconds = 5
            period_seconds       = 10
            timeout_seconds      = 5
          }

          volume_mount {
            name       = "mysql-data"
            mount_path = "/var/lib/mysql"
          }
        }

        volume {
          name = "mysql-data"
          persistent_volume_claim {
            claim_name = "mysql-data"
          }
        }
      }
    }
  }
}

# MySQL Service
resource "kubernetes_service" "mysql" {
  metadata {
    name      = "mysql"
    namespace = kubernetes_namespace.mysql.metadata[0].name
    annotations = {
      "cloud.google.com/load-balancer-type" = "Internal"
    }
  }

  spec {
    selector = {
      app = "mysql"
    }

    port {
      port        = 3306
      target_port = 3306
    }

    type = "LoadBalancer"
  }
}

# Retail Backend Deployment
resource "kubernetes_deployment" "retail_backend" {
  metadata {
    name      = "retail-backend"
    namespace = kubernetes_namespace.retail.metadata[0].name
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "retail-backend"
      }
    }

    template {
      metadata {
        labels = {
          app = "retail-backend"
        }
      }

      spec {
        security_context {
          run_as_user = 1000
        }
        container {
          image = "us-central1-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.retail_backend.name}/${var.backend_image}"
          name  = "retail-backend"

          env {
            name  = "MYSQL_HOST"
            value = kubernetes_service.mysql.status[0].load_balancer[0].ingress[0].ip
          }

          env {
            name  = "MYSQL_USER"
            value = "root"
          }

          env {
            name  = "MYSQL_PORT"
            value = "3306"
          }

          env {
            name  = "MYSQL_PASSWORD"
            value = "${data.google_secret_manager_secret_version.mysql_root_password.secret_data}"
          }

          env {
            name  = "MYSQL_DATABASE"
            value = "retail"
          }

          env {
            name  = "GOOGLE_CLOUD_PROJECT"
            value = var.project_id
          }

          port {
            container_port = 8080
          }

          resources {
            requests = {
              cpu    = "250m"
              memory = "1Gi"
            }
            limits = {
              cpu    = "500m"
              memory = "2Gi"
            }
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = 8080
            }
            initial_delay_seconds = 30
            period_seconds       = 10
            timeout_seconds      = 5
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = 8080
            }
            initial_delay_seconds = 5
            period_seconds       = 10
            timeout_seconds      = 5
          }
        }
      }
    }
  }
}

# Retail Backend Service
resource "kubernetes_service" "retail_backend" {
  metadata {
    name      = "retail-backend"
    namespace = kubernetes_namespace.retail.metadata[0].name
  }

  spec {
    selector = {
      app = "retail-backend"
    }

    port {
      port        = 80
      target_port = 8080
    }

    type = "LoadBalancer"
  }
}

resource "kubernetes_ingress_v1" "backend_ingress" {
  metadata {
    name      = "backend-ingress"
    namespace = kubernetes_namespace.retail.metadata[0].name
    annotations = {
      "kubernetes.io/ingress.class"                 = "gce"
      "networking.gke.io/managed-certificates"      = google_compute_managed_ssl_certificate.website_cert.name
    }
  }

  spec {
    tls {
      hosts = ["api.brendancopp.com"]
    }

    rule {
      host = "api.brendancopp.com"
      http {
        path {
          path      = "/api(/|$)(.*)"
          path_type = "Prefix"

          backend {
            service {
              name = kubernetes_service.retail_backend.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}


# Network Policy for MySQL
resource "kubernetes_network_policy" "mysql" {
  metadata {
    name      = "mysql-network-policy"
    namespace = kubernetes_namespace.mysql.metadata[0].name
  }

  spec {
    pod_selector {
      match_labels = {
        app = "mysql"
      }
    }

    policy_types = ["Ingress"]

    ingress {
      from {
        pod_selector {
          match_labels = {
            app = "retail-backend"
          }
        }
      }
      ports {
        port     = "3306"
        protocol = "TCP"
      }
    }
  }
} 