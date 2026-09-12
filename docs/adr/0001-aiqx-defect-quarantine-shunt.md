# ADR-0001: Sub-50ms AIQX Computer Vision Defect Quarantine Shunting at Line Edge

**Status:** Accepted  
**Date:** 2026-05-27  
**Lead Architect:** William Free Hall (Free) <whall4.wh@gmail.com>

## 1. Context & Operational Challenge
The Spartanburg assembly line operates on a strict 60-second takt time. Automated quality inspection (AIQX) high-resolution camera stations must classify surface paint and panel gap defects and mechanically trigger physical shunt diverters before the chassis moves to the next assembly cell.

## 2. Options Considered
* **Option A: Centralized Cloud Inference over DirectConnect**
  - *Evaluation:* Cloud GPUs offer unlimited compute, but network jitter and round-trip transport time (60-110ms) exceed the 50ms mechanical pneumatic shunt window, causing defective vehicles to pass inspection gates.
* **Option B: Distributed On-Premises Edge Vision Workers with Asynchronous Lakehouse Telemetry**
  - *Evaluation:* Local industrial PC running TensorRT executes inference in 18ms; pneumatic shunt fires instantaneously; defect images and metadata are asynchronously streamed to the Delta Lakehouse.

## 3. Decision & Trade-Off Accepted
We adopted **Option B (Edge Vision with Async Lakehouse Streaming)**.  
**Trade-Off Accepted:** Edge hardware requires physical maintenance; mitigated by automated PXE image recovery and centralized Kubernetes edge fleet management.
