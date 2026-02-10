# Django Audit Log System

A robust, migration‑safe and transaction‑aware audit logging system for Django projects that require reliable tracking of data changes without breaking migrations, tests, or atomic transactions.

---

## Overview

This project provides a stable audit logging layer that safely records Create, Update, Delete and Bulk actions while explicitly avoiding common pitfalls such as:
- signal execution during migrations
- broken database transactions
- noisy or duplicated logs in bulk operations

The system is designed to be **production‑safe**, **migration‑safe**, and **fully test‑covered**.

---

## Why Audit Logging?

Audit logging creates a trustworthy record of **who changed what and when**.

Many existing solutions fail under at least one of these conditions:
- migrations and test database setup
- bulk admin actions
- soft deletes or custom delete logic

This project addresses those gaps by making audit signals explicitly safe and context‑aware.

---

## Core Features

- ✅ **Migration‑Safe Signals**  
  Signals never run on unmanaged/internal Django models or during raw saves.

- ✅ **Transaction‑Safe**  
  Audit logging never breaks `atomic()` blocks.

- ✅ **Bulk Action Support**  
  Django Admin bulk operations are logged correctly and compactly.

- ✅ **Soft‑Delete Compatible**  
  Logical deletions are handled without false positives.

- ✅ **Context‑Based Disable Mechanism**  
  Audit logging can be temporarily disabled (tests, setup, bulk ops).

- ✅ **Fully Tested**  
  24/24 pytest tests passing.

---

## Installation & Setup

1. Copy the `audit_log` app into your Django project.
2. Add it to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
...
"audit_log",
]
