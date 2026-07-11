# Base Subscription Module

The **Hybrid Cloud Base Subscription** defines a minimal set of resources required to stand up an **ISAE 3402-compliant account** accross multiple cloud provider like AWS, GCP, Azure or OCI. It serves as the foundation on which all further provider-specific resources in the resource graph are built. This base module ensures that every account meets baseline organizational and technical requirements for control evidence, auditability, and separation of duties from day one, regardless of the underlying provider.

## Purpose

The common foundation represents a consistent baseline for compliance-relevant account structure (logging, access control, tagging, budget/cost boundaries), ensures a provider-agnostic definition of the minimum required resources, implemented per provider via the respective adapter, provides a foundation for downstream domain controllers (network, IAM, storage, etc.) that build on top of an already-compliant account and enables traceability of configuration as a prerequisite for ISAE audit evidence (compliance-as-code instead of manual evidence gathering). The module is deliberately limited to the essentials: no workload-specific resources, no detailed network design — only what is required for baseline account compliance. Anything beyond that belongs in specialized modules that build on top of this base module.

## Resources

The following resources are defined in the baseline:

### Account Structure
- Clear separation between the management account and workload account (no direct deployment into the root/org account)
- Defined membership in an organizational unit (OU/folder/management group, depending on provider terminology)

### Identity & Access Management
- Baseline roles following the least-privilege principle (e.g., read-only auditor role for compliance checks)
- Mandatory MFA policy for privileged access
- Separation of break-glass access from regular administrative access

### Tagging & Ownership
- Mandatory fields for owner, cost center, and compliance classification at the account level
- Foundation for later mapping to domain controllers within the resource graph

### Policy-as-Code Guardrails
- Deny unauthorized regions or services (deny-by-default for non-approved resources)
- Encryption at rest and in transit enforced as a baseline, not opt-in

### Budget Boundaries
- Cost thresholds with automatic notification
- Quota/limit definitions to guard against misconfiguration

### Auditing & Logging
- Central audit log (immutable, with defined retention period)
- Log forwarding to a central security/compliance account (separate from the workload account)

---

Each of these points is implemented per provider via the corresponding adapter (AWS, GCP, Azure, OCI) — the base module itself defines *what* must exist, not *how* it is technically realized at a given provider.
