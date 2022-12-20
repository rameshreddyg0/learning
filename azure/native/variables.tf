variable "subscription_id" {
  type        = string
  description = "Your Azure Subscription ID"
  default     = "default"
}

variable "client_id" {
  type        = string
  description = "Your Azure Service Principal appId"
  default     = "default"
}

variable "client_secret" {
  type        = string
  description = "Your Azure Service Principal Password"
  default     = "default"
}



variable "tenant_id" {
  type        = string
  description = "Your Azure Tenant ID"
  default     = "default"
}

