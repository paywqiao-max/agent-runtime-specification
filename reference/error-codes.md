# Error Codes

> ARS v1.0 — Error Categories E0–E5  
> Source: Ch5 §5.12

---

## E0 — 本地错误 (Local Error)

**Category**: `E0`  
**HermesException**: `LocalError`  
**Recovery**: Retry 1 time → Report

**Examples**:
- File I/O failure (file not found, permission denied)
- Python execution error
- Tool call failure

---

## E1 — SSH/网络错误 (SSH/Network Error)

**Category**: `E1`  
**HermesException**: `SSHError`  
**Recovery**: Retry 3 times (5s / 30s / 60s intervals) → Report unavailable

**Examples**:
- Connection refused
- Connection timeout
- SSH authentication failure

---

## E2 — 服务器错误 (Server Error)

**Category**: `E2`  
**HermesException**: `ServerError`  
**Recovery**: Stop immediately → Report

**Examples**:
- Conda environment unavailable
- GPU driver error
- Disk full

---

## E3 — 训练/进程错误 (Training/Process Error)

**Category**: `E3`  
**HermesException**: `TrainingError`  
**Recovery**: Diagnose → Attempt auto-recovery (reduce lr, reduce batch) → Report

**Examples**:
- NaN loss during training
- CUDA out of memory (OOM)
- Training process crash

---

## E4 — 逻辑错误 (Logic Error)

**Category**: `E4`  
**HermesException**: `LogicError`  
**Recovery**: Report specific location → User fixes

**Examples**:
- Config syntax error
- Parameter contradiction
- Missing dependency
- Invalid input

---

## E5 — 规范错误 (Specification Error)

**Category**: `E5`  
**HermesException**: `SpecificationError`, `ContractViolation`, `InvariantViolation`  
**Recovery**: Stop execution → Report specification error → Wait for specification fix

**Examples**:
- Broken workflow (cycle, dead end)
- Invalid policy (self-contradictory)
- Schema mismatch
- Unsupported specification version
- Contract violation (AII, WII, VII, IH)
