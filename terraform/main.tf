# ──────────────────────────────────────────────────────────────────
# Terraform — Infraestrutura da Loja Veloz
# Provisiona: VPC, EKS (Kubernetes gerenciado) e RDS (PostgreSQL)
# na AWS. Adaptável para GCP/Azure com módulos equivalentes.
# ──────────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend remoto para estado compartilhado entre a equipe
  backend "s3" {
    bucket         = "loja-veloz-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "loja-veloz-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region
}

# ─── VPC ──────────────────────────────────────────────────────────
module "vpc" {
  source = "./modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  cidr_block         = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

# ─── EKS (Kubernetes gerenciado) ──────────────────────────────────
module "eks" {
  source = "./modules/eks"

  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  cluster_version = "1.28"

  node_groups = {
    general = {
      instance_types = ["t3.medium"]
      min_size       = 2
      max_size       = 10
      desired_size   = 3
    }
  }
}

# ─── RDS — PostgreSQL ─────────────────────────────────────────────
module "rds" {
  source = "./modules/rds"

  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.private_subnet_ids
  db_name           = "pedidosdb"
  db_username       = var.db_username
  db_password       = var.db_password
  instance_class    = "db.t3.micro"
  engine_version    = "15.4"
  multi_az          = var.environment == "prod" ? true : false
}
