## Elevance Health AWS RDS Proxy Module

This module creates AWS RDS Proxy.

## Requirements

1. Secrets manager should be created and the Service ID secrets must be housed in it.

Mandatory Tags Note:
1. As per redesigned new mandatory tags, mandatory tags along with any additional tags have to be added through template configuration within the modules as below
2. Have a reference of mandatory tags module within the template configuration as shown in example script below.

```bash
# Mandatory Tag Workspace Variables
variable "apm-id" {}
variable "application-name" {}
variable "app-support-dl" {}
variable "app-servicenow-group" {}
variable "business-division" {}
variable "company" {}
variable "compliance" {}
variable "costcenter" {}
variable "environment" {}
variable "PatchGroup" {}
variable "PatchWindow" {}
variable "ATLAS_WORKSPACE_NAME" {}

# Mandatory Tags Module 
module "mandatory_tags" {
  source               = "cps-terraform.anthem.com/<ORGANIZATION NAME>/terraform-aws-mandatory-tags-v2/aws"
  tags                 = {}
  apm-id               = var.apm-id
  application-name     = var.application-name
  app-support-dl       = var.app-support-dl
  app-servicenow-group = var.app-servicenow-group
  business-division    = var.business-division
  compliance           = var.compliance
  company              = var.company
  costcenter           = var.costcenter
  environment          = var.environment
  PatchGroup           = var.PatchGroup
  PatchWindow          = var.PatchWindow
  workspace            = var.ATLAS_WORKSPACE_NAME
}

```
3. Mandatory tags module should be referred in tags attribute as below: tags = module.mandatory_tags.tags
4. Any additional tags can be merged to tags attribute as shown : tags = merge(module.mandatory_tags.tags, {"sample" = "abc"})

```bash

## Usage

To run this example you need to execute:

#SAMPLE TEMPLATE FOR RDS PROXY
module "rds_proxy" {
  source = "cps-terraform.anthem.com/<ORGANIZATION NAME>/terraform-aws-rds-proxy/aws"
  name = "members-rds-db-proxy"
  engine_family  = "<DATABASE ENGINE>"
  role_arn       = "arn:aws:iam::<ACCOUNT NUMBER>:role/<ROLE NAME>"
  vpc_subnet_ids = ["<SUBNET-ID-1>", "<SUBNET-ID-2>"]
  auth = [{
    auth_scheme = "SECRETS"
    iam_auth    = "DISABLED"
    secret_arn  = "<SECRETS MANAGER ARN>"
    description = "<DESCRIPTION>"
    username    = null
  }]
  tags = module.mandatory_tags.tags
}

#Initialize Terraform
terraform init

#Terraform Dry-Run
terraform plan

#Create the resources
terraform apply

#Destroy the resources saved in the tfstate
terraform destroy
```

## Providers

| Name | Version |
|------|---------|
| aws | n/a |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| auth | Configuration blocks with authorization mechanisms to connect to the associated instances or clusters. auth\_scheme - The type of authentication that the proxy uses for connections from the proxy to the underlying database. One of SECRETS. client\_password\_auth\_type - The type of authentication the proxy uses for connections from clients. Valid values are MYSQL\_NATIVE\_PASSWORD, POSTGRES\_SCRAM\_SHA\_256, POSTGRES\_MD5, and SQL\_SERVER\_AUTHENTICATION. description - A user-specified description about the authentication used by a proxy to log in as a specific database user. iam\_auth - Whether to require or disallow AWS Identity and Access Management IAM authentication for connections to the proxy. One of DISABLED, REQUIRED. secret\_arn - The Amazon Resource Name ARN representing the secret that the proxy uses to authenticate to the RDS DB instance or Aurora DB cluster. These secrets are stored within Amazon Secrets Manager. username - (Optional) The name of the database user to which the proxy connects. | <pre>list(object({<br>    auth_scheme = string<br>    description = string<br>    iam_auth    = string<br>    secret_arn  = string<br>    username    = string<br>  }))</pre> | `[]` | no |
| debug\_logging | Whether the proxy includes detailed information about SQL statements in its logs. This information helps you to debug issues involving SQL behavior or the performance and scalability of the proxy connections. The debug information includes the text of SQL statements that you submit through the proxy. Thus, only enable this setting when needed for debugging, and only when you have security measures in place to safeguard any sensitive information that appears in the logs. | `string` | `""` | no |
| engine\_family | The kinds of databases that the proxy can connect to. This value determines which database network protocol the proxy recognizes when it interprets network traffic to and from the database. The engine family applies to MySQL and PostgreSQL for both RDS and Aurora. Valid values are MYSQL and POSTGRESQL. | `string` | n/a | yes |
| idle\_client\_timeout | The number of seconds that a connection to the proxy can be inactive before the proxy disconnects it. You can set this value higher or lower than the connection timeout limit for the associated database | `string` | `""` | no |
| name | The identifier for the proxy. This name must be unique for all proxies owned by your AWS account in the specified AWS Region. An identifier must begin with a letter and must contain only ASCII letters, digits, and hyphens; it can't end with a hyphen or contain two consecutive hyphens. | `string` | n/a | yes |
| require\_tls | A Boolean parameter that specifies whether Transport Layer Security (TLS) encryption is required for connections to the proxy. By enabling this setting, you can enforce encrypted TLS connections to the proxy. | `string` | `true` | no |
| role\_arn | The Amazon Resource Name (ARN) of the IAM role that the proxy uses to access secrets in AWS Secrets Manager. | `string` | n/a | yes |
| tags | Key-value map of resource tags | `map(string)` | `{}` | no |
| vpc\_security\_group\_ids | One or more VPC security group IDs to associate with the new proxy. | `list(string)` | `[]` | no |
| vpc\_subnet\_ids | One or more VPC subnet IDs to associate with the new proxy | `list(string)` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| arn | The Amazon Resource Name (ARN) for the proxy. |
| endpoint | The endpoint that you can use to connect to the proxy. You include the endpoint value in the connection string for a database client application. |
| id | The Amazon Resource Name (ARN) for the proxy. |
