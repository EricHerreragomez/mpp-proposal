# MPP Decision Engine

Apply these trees in order. The first matching ROUTE rule wins.

---
## 1. Routing exceptions (check FIRST)

| Topic | Route | Do NOT |
|---|---|---|
| US DSO / Executive Order 14117 | #executive_order_14117-support | send to MPP |
| PSR (Product Security Review) | #psr_support | troubleshoot PSR yourself |
| Pentest | pentesting@mckinsey.com or #pentesting | |
| IRP / Incident Response content | SOC@mckinsey.com (IRP form/Qualtrics issues → IRP support team) | treat Qualtrics errors as MPP issues |
| Accountable Leader / approval routing / leader mapping | tech_risk@mckinsey.com | say AL can be changed |
| SIEM / Infrastructure Asset Logging / IAM / service accounts / certificates / GHD-EXE distribution | #security-ama | |
| Geo IP blocking | sanctions_screening@mckinsey.com | |
| Operational Readiness / Service Offering config | services_readiness@mckinsey.com | |
| Launch Alignment approval | launch@mckinsey.com | |
| Platform McKinsey workspace questions | #platform-mckinsey-help | |
| Cloud decommissioning | #td-sre-cloudconnect | |
| Sunset process questions | #unified_product_catalog | |
| Practice Asset / DPL list | Practice asset governance contact (see kb/09) | create a new Practice Asset to clear the field |
| Data classification | https://techrisk.intranet.mckinsey.com/data-classification-model | classify data yourself |

---
## 2. Can the user self-serve?

```
Is the user (or someone they can reach) the active PM or TL?
├─ YES → give self-service steps (MPP → open product → pencil/Edit → update → review all tabs → Submit)
└─ NO
   ├─ Active PM/TL exists → "Coordinate with the current PM/TL; only they can edit."
   └─ PM/TL inactive / left Firm / ownership or data wrong / no one has edit rights
      → "Scroll to the bottom of the Product page and click *Tell us about wrong data!* — the MPP Team will assist."
```
Exceptions that ALWAYS need the MPP Team (not self-service):
- Pathway changes to/from **Practice Product** or **CCN Tool** (Finance implications)
- Product Pathway changes in general (PM/TL can no longer change pathway directly)

---
## 3. Product vs Project

Register as a Product ONLY IF ALL three are true:
1. Built to deliver value to another user/customer group
2. Active lifecycle — developed, maintained, supported, operated ("hosted indefinitely" ≠ maintained)
3. Ownership — PM, TL, Sponsor (all internal McKinsey employees)

ELSE → **Project Workspace** (Platform McKinsey).

| Project | Product |
|---|---|
| Temporary, study, prototype, demo, experiment, one-off, personal | Reusable, shared, maintained, owned, long-term |

Signals a Project is becoming a Product: reuse across teams/clients, client data processing, need for dedicated Azure Subscription, ongoing support.

---
## 4. Product Workspace vs Project Workspace

```
Needs an Azure Subscription?
├─ YES → requires Product (Product ID) + Product Workspace. Cannot be added to a Project Workspace.
└─ NO  → Project Workspace can use many Platform McKinsey services without a Product ID.

Azure environment by data classification:
├─ Green only           → Azure Sandbox
└─ Yellow or higher     → Azure Analytics Environment (preferred)
```
Migration Project → Product Workspace: see kb/08.

---
## 5. Product Pathway selection

| Pathway | Use when | Mandatory extras |
|---|---|---|
| Practice Product | Built by cell/cell tech group, used in client service, commercially viable (asset fee/chargeback), linked to proprietary asset | **Practice Asset** (existing, dropdown) |
| CCN Tool | Small-scope internal tool, not commercially viable, aids a small part of an internal process | — |
| Deployed Product | Client-specific instance of a source product, maintained by a separate delivery team | **Source Product** |
| Other Product | Built/used by an administrative Firm function to manage its own processes | — |
| CTE Product | Built and maintained by Core Tech Ecosystem members | — |

Other Product and CTE Product are self-service. Changes to/from Practice Product or CCN Tool → MPP Team.

---
## 6. Accountable Leader (AL) — determined automatically, never manually changeable

```
Practice Product      → Practice Asset Ops Lead
CCN Tool              → Sponsoring Group
Deployed Product      → Source Product's AL
Other Product / CTE   → Charge Code → Cost Center → Department Leader (fallback)
```
- Approvers cannot be changed once a registration is submitted; MPP cannot approve on their behalf.
- Stalled approval → open request in My Requests, see who it sits with, contact that approver directly.
- Mapping looks wrong → tech_risk@mckinsey.com.
- Group Engineering Leader: auto-imported from Cost Center Department Code (from Charge Code); refreshes on import (~24h). Still wrong → tech_risk@mckinsey.com.

---
## 7. Charge Code

- Mandatory. Source of truth for **Cost Center, Department, Cell** (derived automatically).
- Must be: active · belong to the user's organization · aligned with the pathway.
- Never recommend selecting a random Cost Center.
- Not actually charged until cloud resources / Platform McKinsey services are consumed (automated billing).
- No Charge Code → check what other products in the same department use, or confirm with Department/Finance lead.
- Sunset: Charge Code must stay valid ≥ 2 more months.
- Can't update / mapping wrong → "Tell us about wrong data!".

---
## 8. Roles & edit rights

| Role | Can edit product? | External worker allowed? |
|---|---|---|
| Product Manager | Yes | No |
| Technical Lead | Yes | No |
| Sponsor | No | No |
| Department Leader | Editor access per KB | No |
| UX roles | No | Yes |
| Security roles | No | Yes |

- IRP: editable only by PM and TL; read-only for everyone else after submission.
- External worker needs edits → work through internal PM/TL, or be added in UX/Security role.

---
## 9. One Product ID or several?

One Product ID if the parts share ALL: ownership · lifecycle · data classification/security posture · Charge Code & AL routing · Service Offering/support routing.
Separate IDs if they diverge on any — especially data classification or ownership (drives PSR cadence, IRP, approvals).
Product versioning is NOT enabled in MPP — scope changes = update the existing record (no re-registration).

---
## 10. Registration in flight

- Product ID is generated at registration, not at approval.
- No "back to draft". Options: let approval complete then edit (preferred for small fixes), or cancel in My Requests and re-submit (restarts approval).
- No documented SLA for registration or Launch Alignment — do not guess. Main bottleneck = AL approval (6+ weeks seen when AL doesn't act).

---
## 11. Environments & sync

| Item | Behavior |
|---|---|
| CMDB sync of tagged resources | ~24 hours |
| Pre-Prod sync | Weekly |
| QA sync | Occasional only → Product IDs needed in QA: raise a request to the PCIS team |
| Mandatory cloud tags | `product_id`, `used_for`, `product_version` |
| `used_for` values | `sbx`, `non_prod`, `prod` |

Dynatrace / reporting: never identify Sandbox/PoC by Product ID (IDs are system-generated, encode nothing). Use `used_for` tag, Lifecycle Status, naming conventions, Platform McK Projects.

---
## 12. Compliance indicators

Requirements come from each product's own record, not shared infra. Drivers: data classification, lifecycle stage, product type/setup, Asset Inventory links.
- PSR cadence: every 6 months for Purple/Red; annually for Yellow/Green.
- MPP cannot change indicator criteria → route to indicator owner (Section 1).

---
## 13. Notifications
- Daily Digest and Weekly Status exist.
- There is NO dedicated PSR expiration notification.
