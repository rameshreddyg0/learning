resource "azurerm_subscription_policy_assignment" "monitoring_governance" {
  name                 = "monitoring_governance"
  subscription_id      = data.azurerm_subscription.current.id
  policy_definition_id = var.monitoring_governance_policyset_id
  description          = "Assignment of the Monitoring Governance initiative to subscription."
  display_name         = "Monitoring Governance"
  location             = "australiaeast"
  identity { type = "SystemAssigned" }
}

resource "azurerm_subscription_policy_assignment" "tag_governance" {
  name                 = "tag_governance"
  subscription_id      = data.azurerm_subscription.current.id
  policy_definition_id = var.tag_governance_policyset_id
  description          = "Assignment of the Tag Governance initiative to subscription."
  display_name         = "Tag Governance"
  location             = "australiaeast"
  identity { type = "SystemAssigned" }
}

resource "azurerm_subscription_policy_assignment" "iam_governance" {
  name                 = "iam_governance"
  subscription_id      = data.azurerm_subscription.current.id
  policy_definition_id = var.iam_governance_policyset_id
  description          = "Assignment of the IAM Governance initiative to subscription."
  display_name         = "Identity and Access Management Governance"
}

resource "azurerm_subscription_policy_assignment" "security_governance" {
  name                 = "security_governance"
  subscription_id      = data.azurerm_subscription.current.id
  policy_definition_id = var.security_governance_policyset_id
  description          = "Assignment of the Security Governance initiative to subscription."
  display_name         = "Security Governance"
  location             = "australiaeast"
  identity { type = "SystemAssigned" }
}

resource "azurerm_subscription_policy_assignment" "data_protection_governance" {
  name                 = "data_protection_governance"
  subscription_id      = data.azurerm_subscription.current.id
  policy_definition_id = var.data_protection_governance_policyset_id
  description          = "Assignment of the Data Protection Governance initiative to subscription."
  display_name         = "Data Protection Governance"
}


resource "azurerm_resource_group_policy_exemption" "exemption_tag_governance" {
  name                 = "exemption_tag_governance"
  count                = length(var.exem_tag_gov_rg_id)
  resource_group_id    = var.exem_tag_gov_rg_id[count.index]
  policy_assignment_id = azurerm_subscription_policy_assignment.tag_governance.id
  exemption_category   = "Mitigated"
}
