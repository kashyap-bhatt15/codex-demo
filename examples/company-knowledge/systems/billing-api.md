---
type: System
title: Billing API
description: Service that issues invoices and charges customers.
resource: https://github.com/example/billing-api
tags: [billing, backend]
status: stable
generated: { by: agent:docs-bot, at: 2026-08-12T09:30:00Z }
verified: { by: agent:consistency-check, at: 2026-08-12T09:45:00Z }
stale_after: 2099-01-01T00:00:00Z
---

## Overview

Owns subscriptions, invoices and payment attempts. Feeds the
[MRR metric](/metrics/monthly-recurring-revenue.md). When a charge fails,
follow the [failed-payment playbook](/playbooks/failed-payment.md).
