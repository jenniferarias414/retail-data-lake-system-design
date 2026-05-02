variable "project_name" {
  description = "Project name used for naming AWS resources."
  type        = string
  default     = "retail-data-lake-poc"
}

variable "aws_region" {
  description = "AWS region where resources will be deployed."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name for tagging resources."
  type        = string
  default     = "dev"
}