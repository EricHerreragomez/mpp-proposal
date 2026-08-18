# MPP Decision Engine (Business Logic Layer)

This document is the single source of truth for routing and decision logic. Code and prompts must
reference this document rather than re-encoding these rules elsewhere.

---

## 1. Special-case routing (check this FIRST, before self-service flow)

| Topic | Route to | Notes |
|---|---|---|
| US DSO | `#executive_order_14117-support` | Do **not** send to MPP. |
| PSR | `#psr_support` | Do not attempt to troubleshoot PSR directly. |
| Pentest | `pentesting@mckinsey.com` or `#pentesting` | |
| QA Product ID visibility | PCIS team (raise a request) | QA sync is occasional, not regular. Pre-Prod syncs weekly. |
| Approval routing questions (Accountable Leader) | `tech_risk@mckinsey.com` | |

If none of these apply, proceed to standard self-service / default escalation flow from the system prompt.

---

## 2. Product vs. Project decision rule

Before recommending Product registration, all three must be true:

1. Built to deliver value to another user/customer group.
2. Has an active lifecycle: developed, maintained, supported, operated.
3. Has ownership: PM, TL, Sponsor.

If **any** are false → recommend a **Project Workspace** instead.

| | Project | Product |
|---|---|---|
| Duration | Temporary | Long-term |
| Nature | Study, prototype, experiment, one-off, personal | Reusable, shared, maintained, owned |

---

## 3. Product Workspace vs. Project Workspace

- **Azure Subscription** requires a **Product** + **Product Workspace**. Cannot be added to a Project Workspace.
- **Project Workspace** can use many Platform McKinsey services without a Product ID.
- **Azure Analytics Environment**: preferred for yellow-or-higher classified data.
- **Azure Sandbox**: green data only.

---

## 4. Product Pathway

Product Pathway can no longer be changed directly by PM/TL. Only the MPP Team performs pathway
updates. If a user asks to change it themselves, direct them to the default escalation flow
("Tell us about wrong data!").

---

## 5. Accountable Leader — selection logic

Never tell a user this can be manually changed. It is determined automatically based on product type:

| Product type | Accountable Leader source |
|---|---|
| Practice Product | Practice Asset Ops Lead |
| CCN Tool | Sponsoring Group |
| Deployed Product | Source Product's AL |
| Other Product / CTE | Charge Code → Cost Center → Department Leader (fallback, in that order) |

Approval routing questions about this logic → `tech_risk@mckinsey.com`.

---

## 6. Charge Code

- Mandatory on every product.
- Drives: Cost Center, Department, Cell.
- Must be: active, belong to the organization, aligned with the Pathway.
- Never recommend selecting a random Cost Center to "get past" a Charge Code requirement.

---

## 7. IRP (editability)

- Editable only by: Product Manager, Technical Lead.
- Everyone else: read-only after submission.

---

## 8. External users — role restrictions

External workers **cannot** be:
- Product Manager
- Technical Lead
- Sponsor
- Department Leader

External workers **can** hold:
- UX roles
- Security roles

---

## 9. Tagging & sync

- Mandatory tags: `product_id`, `used_for`, `product_version`.
- CMDB synchronization: ~24 hours.
- Dynatrace: never identify a Sandbox by Product ID — use `used_for`, Lifecycle, Naming, or Platform McKinsey Projects instead.

---

## 10. Notifications

- Daily Digest and Weekly Status exist.
- There is **no** dedicated PSR expiration notification. Don't imply one exists.

---

## 11. Service Offering taxonomy (for support routing)

Business Application → Application Service → Business Service → Service Offering → Technical
Service → Technical Service Offering. Service Offering is what routes support — point users here
when they ask "who supports this."

---

## 12. Data classification

Always point users to the classification model rather than guessing a data color yourself:
https://techrisk.intranet.mckinsey.com/data-classification-model
