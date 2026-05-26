output "bucket_name" {
  value = aws_s3_bucket.lakehouse.bucket
}

output "warehouse_path" {
  value = "s3://${aws_s3_bucket.lakehouse.bucket}/lakehouse"
}

output "athena_output" {
  value = "s3://${aws_s3_bucket.lakehouse.bucket}/${var.athena_output_prefix}"
}

output "glue_databases" {
  value = [
    aws_glue_catalog_database.bronze.name,
    aws_glue_catalog_database.silver.name,
    aws_glue_catalog_database.gold.name,
  ]
}

output "glue_crawlers" {
  value = [
    aws_glue_crawler.bronze.name,
    aws_glue_crawler.silver.name,
    aws_glue_crawler.gold.name,
  ]
}

output "athena_workgroup" {
  value = aws_athena_workgroup.lakehouse.name
}
