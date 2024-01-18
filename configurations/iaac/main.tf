provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "owwll_rg" {
  name     = "${var.resource_group}_${var.environment}"
  location = "${var.location}"
}

resource "azurerm_container_registry" "owwll_cr" {
  name                = "owwllFastApiCR"
  resource_group_name = azurerm_resource_group.owwll_rg.name
  location            = azurerm_resource_group.owwll_rg.location
  sku                 = "Standard"
}

resource "azurerm_container_group" "owwll_ci" {
  name                = "owwllFastApiCI"
  location            = azurerm_resource_group.owwll_rg.location
  resource_group_name = azurerm_resource_group.owwll_rg.name
  ip_address_type     = "Public"
  os_type             = "Linux"
  restart_policy      = var.restart_policy

  container {
    name   = "owwll-fastapi-container"
    image  = var.image
    cpu    = var.cpu_cores
    memory = var.memory_in_gb

    ports {
      port     = var.port
      protocol = "TCP"
    }
  }
}
