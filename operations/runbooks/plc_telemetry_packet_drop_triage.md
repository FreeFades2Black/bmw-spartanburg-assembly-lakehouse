# Operational Runbook: Diagnosing Assembly Cell PLC Gateway Disconnections

**Severity:** P1 / Assembly Line Halt Risk  
**Target Systems:** Siemens S7 / Rockwell ControlLogix PLC Gateways, OPC-UA Ingest

## Diagnostic Workflow

### 1. Check Plant 10 Line Gateway Connectivity
```bash
ping -c 4 10.140.22.10 # Plant 10 Assembly PLC Gateway
nc -zv 10.140.22.10 4840 # OPC-UA Port
```

### 2. Verify OPC-UA Channel Subscription Status
```bash
python -m src.plc_monitor --probe-gateway 10.140.22.10
```

### 3. Step-by-Step Remediation
1. If packet drops exceed 5%, restart OPC-UA containerized daemon on line controller:
   ```bash
   ssh operator@plant10-edge-04 "sudo systemctl restart opc-ua-collector"
   ```
2. Re-verify ingestion flow into Bronze lakehouse:
   ```bash
   python -m pytest tests/test_bmw_lakehouse.py -v
   ```
