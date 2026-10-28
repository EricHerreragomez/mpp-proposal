# Compliance & Security Indicators

Compliance requirements come from each product's own record (data classification, lifecycle stage, product type/setup, Asset Inventory links) — products on the same infra can legitimately show different requirements.

- PSR cadence: every 6 months for Purple/Red, annually for Yellow/Green.
- Infrastructure asset logging depends on which CIs are linked to each product; shared infra may be linked to only one.
- Geo IP blocking answers differ for third-party SaaS, Firm-only, or centrally managed products.
- Self-Assessment Documents are under Product Details and may have pending questionnaires.

## What to check
1. Open each product in MPP
2. Compare data classification, lifecycle stage, pathway, Self-Assessment Documents
3. Check Asset Inventory links
4. PM/TL fixes wrong fields directly

## Indicator owners (MPP can't change criteria)
| Indicator | Owner |
|---|---|
| PSR | #psr_support |
| Pentest | pentesting@mckinsey.com / #pentesting |
| SIEM / Infrastructure Asset Logging | #security-ama |
| Geo IP blocking | sanctions_screening@mckinsey.com |
| Operational Readiness / Service Offering | services_readiness@mckinsey.com |
| IRP / Incident Response | SOC@mckinsey.com |
| Approval routing / AL | tech_risk@mckinsey.com |
| US DSO (EO 14117) | #executive_order_14117-support |

If products share infra, ownership, lifecycle and classification, consider consolidating into one product (one set of requirements).
