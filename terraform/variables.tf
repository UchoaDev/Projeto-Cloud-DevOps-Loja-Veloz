variable "aws_region" {
  description = "Região AWS para provisionar a infraestrutura"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "loja-veloz"
}

variable "environment" {
  description = "Ambiente: dev | staging | prod"
  type        = string
  default     = "prod"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment deve ser dev, staging ou prod."
  }
}

variable "db_username" {
  description = "Usuário do banco de dados PostgreSQL"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Senha do banco de dados PostgreSQL"
  type        = string
  sensitive   = true
}
