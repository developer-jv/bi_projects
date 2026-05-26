module "lakehouse" {
  source                = "../../modules/lakehouse"
  project_name          = var.project_name
  environment           = var.environment
  aws_region            = var.aws_region
  bucket_name           = var.bucket_name
  glue_crawler_role_arn = var.glue_crawler_role_arn
  athena_output_prefix  = "athena-results/"
  tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}
