resource "aws_s3_bucket" "lakehouse" {
  bucket = var.bucket_name
  tags   = merge(var.tags, { Name = var.bucket_name })
}

resource "aws_s3_bucket_versioning" "lakehouse" {
  bucket = aws_s3_bucket.lakehouse.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lakehouse" {
  bucket = aws_s3_bucket.lakehouse.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "lakehouse" {
  bucket                  = aws_s3_bucket.lakehouse.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_glue_catalog_database" "bronze" {
  name = "bronze"
}

resource "aws_glue_catalog_database" "silver" {
  name = "silver"
}

resource "aws_glue_catalog_database" "gold" {
  name = "gold"
}

resource "aws_glue_crawler" "bronze" {
  name          = "lakehouse-bronze"
  database_name = aws_glue_catalog_database.bronze.name
  role          = var.glue_crawler_role_arn

  s3_target {
    path = "s3://${aws_s3_bucket.lakehouse.bucket}/bronze/"
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  tags = var.tags
}

resource "aws_glue_crawler" "silver" {
  name          = "lakehouse-silver"
  database_name = aws_glue_catalog_database.silver.name
  role          = var.glue_crawler_role_arn

  s3_target {
    path = "s3://${aws_s3_bucket.lakehouse.bucket}/lakehouse/silver.db/"
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  tags = var.tags
}

resource "aws_glue_crawler" "gold" {
  name          = "lakehouse-gold"
  database_name = aws_glue_catalog_database.gold.name
  role          = var.glue_crawler_role_arn

  s3_target {
    path = "s3://${aws_s3_bucket.lakehouse.bucket}/lakehouse/gold.db/"
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  tags = var.tags
}

resource "aws_athena_workgroup" "lakehouse" {
  name = "lakehouse-analytics"

  configuration {
    enforce_workgroup_configuration = true
    result_configuration {
      output_location = "s3://${aws_s3_bucket.lakehouse.bucket}/${var.athena_output_prefix}"
    }
  }

  tags = var.tags
}
