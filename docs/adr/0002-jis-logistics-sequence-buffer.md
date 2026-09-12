# ADR-0002: Just-in-Sequence (JIS) Logistics Buffer Synchronization in Silver Delta Marts

**Status:** Accepted  
**Date:** 2026-06-16  
**Lead Architect:** William Free Hall (Free) <whall4.wh@gmail.com>

## 1. Context & Operational Challenge
Just-in-Sequence (JIS) manufacturing delivers vehicle-specific components (custom cockpits, wiring harnesses) to the line exactly in the sequence vehicles arrive. When a vehicle is quarantined for defect rework, downstream supplier sequencing signals must adjust immediately.

## 2. Options Considered
* **Option A: Direct Point-to-Point Supplier Webhooks from Edge PLC**
  - *Evaluation:* Fragile architecture; a supplier network glitch drops sequence signals with zero centralized audit history or replayability.
* **Option B: Event-Driven Delta Lake Change Data Feed (CDF) Streaming**
  - *Evaluation:* Quarantine actions committed to Silver Delta tables emit CDC events; downstream Kafka connectors stream re-sequencing manifests to tier-1 suppliers with persistent offset tracking.

## 3. Decision & Trade-Off Accepted
We adopted **Option B (Delta Lake CDF Streaming)**.  
**Trade-Off Accepted:** Introduces a ~1.5 second pipeline latency between physical quarantine and supplier signal; well within the 12-minute logistics advance buffer window.
