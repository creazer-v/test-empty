data "aws_kms_key" "this" {
  count  = var.number_of_instances > 0 ? 1 : 0
  key_id = var.kms_key_id
}

resource "time_static" "unix_time" {}

resource "aws_instance" "afhuif2" {
  count                                = var.number_of_instances
  ami                                  = var.instance_ami
  instance_type                        = var.instance_type
  iam_instance_profile                 = var.iam_instance_profile
  associate_public_ip_address          = length(var.network_interface_id) != 0 ? null : false
  vpc_security_group_ids               = length(var.network_interface_id) != 0 ? null : var.vpc_security_group_ids
  monitoring                           = var.monitoring
  subnet_id                            = length(var.network_interface_id) != 0 ? null : element(var.subnet_ids, count.index)
  source_dest_check                    = length(var.network_interface_id) != 0 ? null : var.source_dest_check
  tenancy                              = var.tenancy
  instance_initiated_shutdown_behavior = var.instance_initiated_shutdown_behavior
  user_data                            = var.user_data
  disable_api_termination              = var.disable_api_termination
  host_id                              = var.host_id
  ebs_optimized                        = var.ebs_optimized
  hibernation                          = var.hibernation


  root_block_device {
    volume_size           = var.root_volume_size
    delete_on_termination = var.delete_on_termination
    encrypted             = true
    iops                  = var.root_volume_iops
    volume_type           = var.root_volume_type
    kms_key_id            = data.aws_kms_key.this.*.id == null ? "KMS Key is not valid" : var.kms_key_id
    throughput            = var.throughput
  }

  dynamic "ebs_block_device" {
    for_each = var.ebs_block_device != null ? var.ebs_block_device : []
    content {
      delete_on_termination = lookup(ebs_block_device.value, "delete_on_termination", null)
      device_name           = ebs_block_device.value.device_name
      encrypted             = true
      iops                  = lookup(ebs_block_device.value, "iops", null)
      kms_key_id            = data.aws_kms_key.this.*.id == null ? "KMS Key is not valid" : var.kms_key_id
      snapshot_id           = lookup(ebs_block_device.value, "snapshot_id", null)
      volume_size           = lookup(ebs_block_device.value, "volume_size", null)
      volume_type           = lookup(ebs_block_device.value, "volume_type", null)
    }
  }

  dynamic "ephemeral_block_device" {
    for_each = var.ephemeral_block_device != null ? var.ephemeral_block_device : []
    content {
      device_name  = ephemeral_block_device.value.device_name
      no_device    = lookup(ephemeral_block_device.value, "no_device", null)
      virtual_name = lookup(ephemeral_block_device.value, "virtual_name", null)
    }
  }
  enclave_options {
    enabled = var.enclave_enabled
  }
  maintenance_options {
    auto_recovery = var.auto_recovery
  }

  dynamic "capacity_reservation_specification" {
    for_each = var.capacity_reservation_specification != [] ? var.capacity_reservation_specification : []
    content {
      capacity_reservation_preference = var.capacity_reservation_target == [] ? lookup(capacity_reservation_specification.value, "capacity_reservation_preference", null) : null
      dynamic "capacity_reservation_target" {
        for_each = (var.capacity_reservation_target != [] && lookup(capacity_reservation_specification.value, "capacity_reservation_preference") == null) ? var.capacity_reservation_target : []
        content {
          capacity_reservation_id                 = lookup(capacity_reservation_target.value, "capacity_reservation_id", null)
          capacity_reservation_resource_group_arn = lookup(capacity_reservation_target.value, "capacity_reservation_resource_group_arn", null)
        }
      }
    }
  }

  credit_specification {
    cpu_credits = var.cpu_credits
  }
  dynamic "network_interface" {
    for_each = length(var.network_interface_id) == 0 ? [] : [1]
    content {
      device_index          = 0
      network_interface_id  = element(var.network_interface_id, count.index)
      delete_on_termination = var.delete_on_termination_eni
      network_card_index    = var.network_card_index
    }
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = var.http_tokens
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  lifecycle {
    ignore_changes = [
      private_ip,
      ebs_block_device,
      ami,
    ]
  }
  volume_tags = merge(var.tags, {"vol_nm" = "${var.tags["application-name"]}_${time_static.unix_time.unix}"})
  tags        = merge(var.tags,{ "Name" = "${var.instance_name}${count.index + 1}" })
}

