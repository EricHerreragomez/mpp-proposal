# Pre-Ship Checklist

Complete all items below before inviting the MPP Slack Assistant to a shared support channel.

## 1. Tech Risk / workspace admin sign-off

Start this early — in parallel with Slack app setup, not after the bot is built.

A bot that gives governance and escalation guidance in Slack needs the same review any internal tool touching product security/governance would get. Do not install to a production workspace or invite the bot to shared channels without approval.

## 2. IRP definition

`docs/03-knowledge-base.md` contains a deliberate placeholder for IRP's full expansion. Fill this from official MPP documentation before shipping.

The bot must not answer IRP questions with an incomplete glossary entry — that risks contradicting the "never guess" rule in the system prompt.

## 3. Private test channel + six test cases

Deploy to a **private test channel** first. Run all six test cases from `00-BUILD-GUIDE.md` Step 4 and confirm responses match `docs/02-decision-engine.md` exactly:

1. "How do I register a new product?" → self-service flow, MPP link, decision rule questions
2. "My PM is inactive and I can't edit the product." → "Tell us about wrong data!" flow, not a ServiceNow incident
3. "I need help with US DSO." → routes to `#executive_order_14117-support`, not MPP
4. "Can I change the Accountable Leader manually?" → "No, this is determined automatically," explains selection logic
5. "I need a Product ID showing up in QA." → explains QA sync is occasional, routes to PCIS team
6. Ambiguous case: "I built a script for my own analysis, should I register it as a product?" → Project Workspace recommendation, using the three-question test

Only after all six pass and items 1–2 are complete should you open the bot to a broader audience.
