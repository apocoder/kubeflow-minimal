terraform {
  # Terraform CLI 1.5.x ile uyumlu
  required_version = ">= 1.5.0, < 2.0.0"

  required_providers {
    google = {
      source = "hashicorp/google"
      # 1.5.x ile sorunsuz 5.x serisine pinliyoruz
      version = "~> 5.40"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_client_config" "default" {}
