variable "aws_region" {
  type = string
}

variable "aws_access_key_id" {
  type      = string
  sensitive = true
}

variable "aws_secret_access_key" {
  type      = string
  sensitive = true
}

variable "glue_crawler_role_arn" {
  type = string
}

variable "project_name" {
  type    = string
  default = "lakehouse-medallion"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "bucket_name" {
  type = string
}
