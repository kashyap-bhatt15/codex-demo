---
type: Metric
title: Monthly Recurring Revenue
description: Contracted recurring revenue normalized to one month.
resource: https://analytics.example.com/mrr
tags: [finance, saas, board]
status: stable
generated: { by: human:finance-owner, at: 2026-08-12T09:00:00Z }
verified: { by: human:controller, at: 2026-08-12T10:00:00Z }
stale_after: 2099-01-01T00:00:00Z
sources:
  - id: finance-policy
    resource: https://docs.example.com/finance/mrr
    title: Finance policy
---

## Definition

MRR includes active subscriptions and excludes one-off services.[^finance-policy]

It is computed from invoices emitted by the [billing API](/systems/billing-api.md).
Failed charges are handled per the [failed-payment playbook](../playbooks/failed-payment.md).

[^finance-policy]: Finance policy
