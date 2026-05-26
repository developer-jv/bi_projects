variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "bucket_name" {
  type = string
}

variable "glue_crawler_role_arn" {
  type = string
}

variable "athena_output_prefix" {
  type = string
  default = "athena-results/"
}

variable "tags" {
  type = map(string)
  default = {}
}
