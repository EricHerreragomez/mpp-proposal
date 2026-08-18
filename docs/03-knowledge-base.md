# MPP Knowledge Base (Reference Layer)

Factual reference material. Update this file when links, timings, or definitions change — do not
edit the Decision Engine for pure fact changes.

## Key links

- My Product Portal home: https://mckinsey.service-now.com/products?id=my_product_home&spa=1&tab=dept
- Data classification model: https://techrisk.intranet.mckinsey.com/data-classification-model

## Escalation contacts / channels

- US DSO: `#executive_order_14117-support`
- PSR: `#psr_support`
- Pentest: `pentesting@mckinsey.com`, `#pentesting`
- Accountable Leader approval routing: `tech_risk@mckinsey.com`
- Product ID issues in QA: PCIS team
- General MPP data issues: "Tell us about wrong data!" button at the bottom of the Product page

## Sync timings

- CMDB synchronization: ~24 hours
- Pre-Prod environment sync: weekly
- QA environment sync: occasional, not on a fixed schedule

## Service Offering hierarchy (reference)

Business Application → Application Service → Business Service → Service Offering → Technical
Service → Technical Service Offering.

- **Service Offering** is the layer that determines support routing.

## Environment / data classification quick reference

- Azure Sandbox: green data only.
- Azure Analytics Environment: preferred for yellow-or-higher classified data.
- Always confirm exact classification via the data classification model link above rather than
  assuming from context.

## Notifications available

- Daily Digest
- Weekly Status
- (No dedicated PSR expiration notification exists.)

## Mandatory tags

- `product_id`
- `used_for`
- `product_version`

## Glossary

- **PM** — Product Manager
- **TL** — Technical Lead
- **AL** — Accountable Leader
- **IRP** — [document exact expansion/definition here once confirmed; currently referenced only as
  an editable-by-PM/TL record type in governance docs]
- **PSR** — Product Security Review (routed, not self-serviced)
- **CTE** — Product/charge-code-driven "Other Product" category (see Decision Engine §5)
- **CCN Tool** — Product type whose Accountable Leader is the Sponsoring Group

> Note: keep this glossary factual and sourced from official MPP documentation. If a term's full
> definition isn't confirmed, leave a placeholder rather than guessing — per the "never speculate"
> rule in the system prompt.
