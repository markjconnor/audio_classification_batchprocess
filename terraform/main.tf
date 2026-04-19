# Interpret namespace and network name based on user name
locals {
  namespace = "${var.username}-comp0235-ns"
  network_name = "${var.username}-comp0235-ns/ds4eng"
}

data "harvester_image" "img" {
  display_name = var.img_display_name
  namespace    = "harvester-public"
}

data "harvester_ssh_key" "mysshkey" {
  name      = var.keyname
  namespace = local.namespace
}

resource "random_id" "secret" {
  byte_length = 5
}

resource "harvester_cloudinit_secret" "cloud-config" {
  name      = "cloud-config-${random_id.secret.hex}"
  namespace = local.namespace

  user_data = templatefile("cloud-init.tmpl.yml", {
      public_key_openssh = data.harvester_ssh_key.mysshkey.public_key
    })
}

resource "harvester_virtualmachine" "host" {
  
  count = 1

  name                 = "${var.username}-host-${format("%02d", count.index + 1)}-${random_id.secret.hex}"
  namespace            = local.namespace
  restart_after_update = true

  description = "Cluster Host Node"

  cpu    = 2
  memory = "10Gi"

  efi         = true
  secure_boot = false

  run_strategy    = "RerunOnFailure"
  hostname        = "${var.username}-host-${format("%02d", count.index + 1)}-${random_id.secret.hex}"
  reserved_memory = "100Mi"
  machine_type    = "q35"

  network_interface {
    name           = "nic-1"
    wait_for_lease = true
    type           = "bridge"
    network_name   = local.network_name
  }

  disk {
    name       = "rootdisk"
    type       = "disk"
    size       = "10Gi"
    bus        = "virtio"
    boot_order = 1

    image       = data.harvester_image.img.id
    auto_delete = true
  }

  cloudinit {
    user_data_secret_name = harvester_cloudinit_secret.cloud-config.name
  }

  tags = {
    condenser_ingress_isEnabled = true
    condenser_ingress_prometheus_hostname = "prometheus-${var.username}"
    condenser_ingress_prometheus_port = 9090
    condenser_ingress_prometheus_protocol = "http"
    condenser_ingress_httpd_hostname = "website-${var.username}"
    condenser_ingress_httpd_port = 80
    condener_ingress_httpd_protocol = "http"
  }

  timeouts {
    create = "20m"
    update = "20m"
    delete = "20m"
  }

}

resource "harvester_virtualmachine" "workervm" {
  
  count = var.vm_count

  name                 = "${var.username}-worker-${format("%02d", count.index + 1)}-${random_id.secret.hex}"
  namespace            = local.namespace
  restart_after_update = true

  description = "Cluster Compute Node"

  cpu    = 5
  memory = "32Gi"

  efi         = true
  secure_boot = false

  run_strategy    = "RerunOnFailure"
  hostname        = "${var.username}-worker-${format("%02d", count.index + 1)}-${random_id.secret.hex}"
  reserved_memory = "100Mi"
  machine_type    = "q35"

  network_interface {
    name           = "nic-1"
    wait_for_lease = true
    type           = "bridge"
    network_name   = local.network_name
  }

  disk {
    name       = "rootdisk"
    type       = "disk"
    size       = "120Gi"
    bus        = "virtio"
    boot_order = 1

    image       = data.harvester_image.img.id
    auto_delete = true
  }

  cloudinit {
    user_data_secret_name = harvester_cloudinit_secret.cloud-config.name
  }

  tags = {
    condenser_ingress_isEnabled = true
    condenser_ingress_node_exporter_hostname = "${var.username}-node-exporter${format("%02d", count.index + 1)}"
    condenser_ingress_node_exporter_port = 9100
    condenser_ingress_node_exporter_protocol = "http"
  }

  timeouts {
    create = "20m"
    update = "20m"
    delete = "20m"
  }

}

resource "local_file" "ansible_hosts" {
  # 1. THE PATH: Where should Terraform save the file?
  # This example assumes your 'ansible' folder is sitting right next to your terraform folder.
  filename = "${path.module}/../ansible/hosts"

  content = templatefile("${path.module}/hosts.tmpl", {
    # 2. THE RESOURCES: These must match exactly what you named your VMs higher up in main.tf
    host_ip    = harvester_virtualmachine.host[0].network_interface[0].ip_address
    worker_ips = [for vm in harvester_virtualmachine.workervm : vm.network_interface[0].ip_address]
  })
}
