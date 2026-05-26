output "bucket_name" {
  value = module.lakehouse.bucket_name
}

output "warehouse_path" {
  value = module.lakehouse.warehouse_path
}

output "athena_output" {
  value = module.lakehouse.athena_output
}

output "glue_databases" {
  value = module.lakehouse.glue_databases
}

output "glue_crawlers" {
  value = module.lakehouse.glue_crawlers
}

output "athena_workgroup" {
  value = module.lakehouse.athena_workgroup
}
