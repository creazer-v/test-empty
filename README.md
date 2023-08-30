<!-- BEGIN_TF_DOCS -->
## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_log_group.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_db_proxy.db_proxy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_proxy) | resource |
| [aws_db_proxy_default_target_group.default_target_group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_proxy_default_target_group) | resource |
| [aws_db_proxy_target.db_proxy_target](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_proxy_target) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_auth"></a> [auth](#input\_auth) | Configuration blocks with authorization mechanisms to connect to the associated instances or clusters. auth\_scheme - The type of authentication that the proxy uses for connections from the proxy to the underlying database. One of SECRETS. client\_password\_auth\_type - The type of authentication the proxy uses for connections from clients. Valid values are MYSQL\_NATIVE\_PASSWORD, POSTGRES\_SCRAM\_SHA\_256, POSTGRES\_MD5, and SQL\_SERVER\_AUTHENTICATION. description - A user-specified description about the authentication used by a proxy to log in as a specific database user. iam\_auth - Whether to require or disallow AWS Identity and Access Management IAM authentication for connections to the proxy. One of DISABLED, REQUIRED. secret\_arn - The Amazon Resource Name ARN representing the secret that the proxy uses to authenticate to the RDS DB instance or Aurora DB cluster. These secrets are stored within Amazon Secrets Manager. username - (Optional) The name of the database user to which the proxy connects. | <pre>list(object({<br>    auth_scheme = string<br>    description = string<br>    iam_auth    = string<br>    secret_arn  = string<br>    username    = string<br>  }))</pre> | `[]` | no |
| <a name="input_connection_borrow_timeout"></a> [connection\_borrow\_timeout](#input\_connection\_borrow\_timeout) | The number of seconds for a proxy to wait for a connection to become available in the connection pool | `number` | `null` | no |
| <a name="input_db_cluster_identifier"></a> [db\_cluster\_identifier](#input\_db\_cluster\_identifier) | DB cluster identifier | `string` | `""` | no |
| <a name="input_db_instance_identifier"></a> [db\_instance\_identifier](#input\_db\_instance\_identifier) | DB instance identifier | `string` | `""` | no |
| <a name="input_debug_logging"></a> [debug\_logging](#input\_debug\_logging) | Whether the proxy includes detailed information about SQL statements in its logs. This information helps you to debug issues involving SQL behavior or the performance and scalability of the proxy connections. The debug information includes the text of SQL statements that you submit through the proxy. Thus, only enable this setting when needed for debugging, and only when you have security measures in place to safeguard any sensitive information that appears in the logs. | `string` | `""` | no |
| <a name="input_engine_family"></a> [engine\_family](#input\_engine\_family) | The kinds of databases that the proxy can connect to. This value determines which database network protocol the proxy recognizes when it interprets network traffic to and from the database. The engine family applies to MySQL and PostgreSQL for both RDS and Aurora. Valid values are MYSQL and POSTGRESQL. | `string` | n/a | yes |
| <a name="input_idle_client_timeout"></a> [idle\_client\_timeout](#input\_idle\_client\_timeout) | The number of seconds that a connection to the proxy can be inactive before the proxy disconnects it. You can set this value higher or lower than the connection timeout limit for the associated database | `string` | `""` | no |
| <a name="input_init_query"></a> [init\_query](#input\_init\_query) | One or more SQL statements for the proxy to run when opening each new database connection | `string` | `""` | no |
| <a name="input_kms_key_id_log_group"></a> [kms\_key\_id\_log\_group](#input\_kms\_key\_id\_log\_group) | The ARN for the KMS encryption key for RDS Log Group. | `string` | n/a | yes |
| <a name="input_max_connections_percent"></a> [max\_connections\_percent](#input\_max\_connections\_percent) | The maximum size of the connection pool for each target in a target group | `number` | `90` | no |
| <a name="input_max_idle_connections_percent"></a> [max\_idle\_connections\_percent](#input\_max\_idle\_connections\_percent) | Controls how actively the proxy closes idle database connections in the connection pool | `number` | `50` | no |
| <a name="input_name"></a> [name](#input\_name) | The identifier for the proxy. This name must be unique for all proxies owned by your AWS account in the specified AWS Region. An identifier must begin with a letter and must contain only ASCII letters, digits, and hyphens; it can't end with a hyphen or contain two consecutive hyphens. | `string` | n/a | yes |
| <a name="input_require_tls"></a> [require\_tls](#input\_require\_tls) | A Boolean parameter that specifies whether Transport Layer Security (TLS) encryption is required for connections to the proxy. By enabling this setting, you can enforce encrypted TLS connections to the proxy. | `string` | `true` | no |
| <a name="input_retention_in_days_rds_proxy"></a> [retention\_in\_days\_rds\_proxy](#input\_retention\_in\_days\_rds\_proxy) | Specifies the number of days you want to retain Audit log events in the specified log group. Possible values are: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653, and 0. If you select 0, the events in the Audit log group are always retained and never expire. | `number` | `7` | no |
| <a name="input_role_arn"></a> [role\_arn](#input\_role\_arn) | The Amazon Resource Name (ARN) of the IAM role that the proxy uses to access secrets in AWS Secrets Manager. | `string` | n/a | yes |
| <a name="input_session_pinning_filters"></a> [session\_pinning\_filters](#input\_session\_pinning\_filters) | Each item in the list represents a class of SQL operations that normally cause all later statements in a session using a proxy to be pinned to the same underlying database connection | `list(string)` | `[]` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Key-value map of resource tags | `map(string)` | `{}` | no |
| <a name="input_vpc_security_group_ids"></a> [vpc\_security\_group\_ids](#input\_vpc\_security\_group\_ids) | One or more VPC security group IDs to associate with the new proxy. | `list(string)` | `[]` | no |
| <a name="input_vpc_subnet_ids"></a> [vpc\_subnet\_ids](#input\_vpc\_subnet\_ids) | One or more VPC subnet IDs to associate with the new proxy | `list(string)` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_arn"></a> [arn](#output\_arn) | The Amazon Resource Name (ARN) for the proxy. |
| <a name="output_endpoint"></a> [endpoint](#output\_endpoint) | The endpoint that you can use to connect to the proxy. You include the endpoint value in the connection string for a database client application. |
| <a name="output_id"></a> [id](#output\_id) | The Amazon Resource Name (ARN) for the proxy. |
| <a name="output_log_group_arn"></a> [log\_group\_arn](#output\_log\_group\_arn) | The Amazon Resource Name (ARN) of the CloudWatch log group |
| <a name="output_proxy_default_target_group_arn"></a> [proxy\_default\_target\_group\_arn](#output\_proxy\_default\_target\_group\_arn) | The ARN for the default target group |
| <a name="output_proxy_default_target_group_id"></a> [proxy\_default\_target\_group\_id](#output\_proxy\_default\_target\_group\_id) | The ID for the default target group |
| <a name="output_proxy_default_target_group_name"></a> [proxy\_default\_target\_group\_name](#output\_proxy\_default\_target\_group\_name) | The ARN for the default target group |
| <a name="output_proxy_target_target_arn"></a> [proxy\_target\_target\_arn](#output\_proxy\_target\_target\_arn) | Amazon Resource Name (ARN) for the DB instance or DB cluster. Currently not returned by the RDS API |
| <a name="output_proxy_target_target_id"></a> [proxy\_target\_target\_id](#output\_proxy\_target\_target\_id) | Identifier of `db_proxy_name`, `target_group_name`, target type (e.g. `RDS_INSTANCE` or `TRACKED_CLUSTER`), and resource identifier separated by forward slashes (/) |
<!-- END_TF_DOCS -->
