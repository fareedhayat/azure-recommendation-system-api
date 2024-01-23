provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "owwll_rg" {
  name     = "${var.resource_group}_${var.environment}"
  location = "${var.location}"
}

resource "azurerm_container_registry" "owwll_cr" {
  name                = "owwllFastApiCR"
  admin_enabled = true
  resource_group_name = azurerm_resource_group.owwll_rg.name
  location            = azurerm_resource_group.owwll_rg.location
  sku                 = "Standard"
}



