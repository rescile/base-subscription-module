# Hybrid Cloud Base Module

The **Hybrid Cloud Base Module** defines the minimal, provider-agnostic set of resources required to stand up an **ISAE 3402-compliant account** with any cloud provider (AWS, GCP, Azure, OCI) — serving as the declarative foundation on which all further domain-specific resources in the resource graph are built.

It ensures that every newly created account meets baseline organizational and technical requirements for control evidence, auditability, and separation of duties from day one — regardless of the underlying provider.

## Purpose

- Consistent baseline for compliance-relevant account structure (logging, access control, tagging, budget/cost boundaries)
- Provider-agnostic definition of the minimum required resources, implemented per provider via the respective adapter
- Foundation for downstream domain controllers (network, IAM, storage, etc.) that build on top of an already-compliant account
- Traceability of configuration as a prerequisite for ISAE audit evidence (compliance-as-code instead of manual evidence gathering)

## Scope

The module is deliberately limited to the essentials: no workload-specific resources, no detailed network design — only what is required for baseline account compliance. Anything beyond that belongs in specialized modules that build on top of this base module.

## Provider-Agnostic Resources

### Audit & Logging
- Central audit log (immutable, with defined retention period)
- Log forwarding to a central security/compliance account (separate from the workload account)

### Identity & Access Baseline
- Baseline roles following the least-privilege principle (e.g., read-only auditor role for compliance checks)
- Mandatory MFA policy for privileged access
- Separation of break-glass access from regular administrative access

### Guardrails / Policy-as-Code
- Deny unauthorized regions or services (deny-by-default for non-approved resources)
- Encryption at rest and in transit enforced as a baseline, not opt-in

### Tagging & Ownership
- Mandatory fields for owner, cost center, and compliance classification at the account level
- Foundation for later mapping to domain controllers within the resource graph

### Budget & Boundaries
- Cost thresholds with automatic notification
- Quota/limit definitions to guard against misconfiguration

### Account Structure
- Clear separation between the management account and workload account (no direct deployment into the root/org account)
- Defined membership in an organizational unit (OU/folder/management group, depending on provider terminology)

---

Each of these points is implemented per provider via the corresponding adapter (AWS, GCP, Azure, OCI) — the base module itself defines *what* must exist, not *how* it is technically realized at a given provider.
