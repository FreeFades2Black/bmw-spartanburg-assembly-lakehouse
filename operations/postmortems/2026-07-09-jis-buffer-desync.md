# Incident Post-Mortem: Chassis Quarantine Shunt Causing Downstream JIS Sequence Inversion

**Incident Date:** 2026-07-09  
**Impact Duration:** 21 minutes  
**Severity:** SEV-2  
**Root Cause:** A paint defect shunt shunted chassis #4092 off the main line into rework. The Delta Lake Change Data Feed consumer crashed due to an unhandled null VIN exception, failing to notify the seat supplier of the sequence gap.

## Timeline
* **13:40 UTC:** Chassis #4092 shunted to rework lane.
* **13:42 UTC:** CDF consumer crashed with `AttributeError: 'NoneType' object has no attribute 'vin'`.
* **13:51 UTC:** Cockpit marriage station halted when component barcode #4092 did not match arriving vehicle #4093.
* **13:56 UTC:** On-call engineer deployed hotfix with defensive null checks and manual sequence offset skip.
* **14:01 UTC:** Conveyor restarted; sequence synchronized.

## Corrective Actions
1. Added Pydantic strict schema validation in `test_bmw_lakehouse.py` preventing null VIN fields from being emitted by edge PLC handlers.
2. Implemented automated optical VIN barcode scanner verification prior to component marriage cells.
