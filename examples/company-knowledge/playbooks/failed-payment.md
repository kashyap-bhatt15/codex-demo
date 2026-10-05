---
type: Playbook
title: Handle a failed payment
description: Steps for support when a customer charge fails.
tags: [billing, support]
status: draft
---

## Steps

1. Look up the invoice in the [billing API](/systems/billing-api.md).
2. Retry once after 24h; email the customer on the second failure.
3. Escalate refunds to finance (see the [refund policy](/playbooks/refunds.md)).
