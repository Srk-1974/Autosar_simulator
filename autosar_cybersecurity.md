# 🛡️ Module 7: AUTOSAR Cybersecurity (SecOC & CSM)

With modern vehicles being connected to the internet, cybersecurity is no longer optional. This module covers how AUTOSAR secures in-vehicle networks against spoofing, replay attacks, and unauthorized access.

---

## 🎯 Learning Objectives
- [ ] Understand the AUTOSAR Crypto Stack (CSM, CryIf, Crypto drivers)
- [ ] Implement Secure Onboard Communication (SecOC)
- [ ] Configure Message Authentication Codes (MAC) and Freshness Values (FV)
- [ ] Prevent Replay Attacks and Bus Spoofing
- [ ] Implement Secure Diagnostics Authentication (UDS 0x29)

---

## 📚 Theory: The AUTOSAR Security Architecture

### 1. SecOC (Secure Onboard Communication)
SecOC sits between the **PduR (PDU Router)** and the **Com** module. Its job is to ensure that critical signals (e.g., "Deploy Airbag" or "Brake Now") are **Authentic** and **Fresh**.

**How it works:**
Instead of just sending `[DATA]`, SecOC sends `[DATA] + [Freshness Value] + [MAC]`.
*   **MAC (Message Authentication Code):** A cryptographic hash proving the sender knows the secret key.
*   **Freshness Value (FV):** A counter or timestamp proving the message is new (prevents replay attacks).

```
   Normal CAN Frame: [ ID: 0x100 | Length: 8 | 01 02 03 04 05 06 07 08 ]
   SecOC CAN Frame:  [ ID: 0x100 | Length: 8 | 01 02 03 (Data) | 1A 2B (FV) | 9F 4C 8D (MAC) ]
```

### 2. The Crypto Stack Hierarchy
```
    [ Application SWC ]  ← Uses CSM via RTE
            │
            ▼
    [ CSM (Crypto Service Manager) ] ← Standardized Crypto API
            │
            ▼
    [ CryIf (Crypto Interface) ] ← Routes requests to hardware/software
            │
            ▼
    [ Crypto Driver (MCAL) ] ← Hardware Security Module (HSM) / SHE
```

---

## 💻 Lab 7A: SecOC Configuration & MAC Generation

In this lab, we configure a critical PDU (Brake Command) to be secured using AES-128 CMAC.

### 1. SecOC Tx (Transmission) Flow
When the Brake SWC sends a command, SecOC intercepts it, asks CSM to calculate the MAC, appends it, and sends it to the CAN bus.

```c
/* SecOC_Callouts.c */
#include "SecOC.h"
#include "Csm.h"

/* 
 * Callout: Get Freshness Value 
 * In production, this uses a complex time-sync or counter mechanism.
 */
Std_ReturnType SecOC_GetTxFreshness(
    uint16 freshnessValueId, 
    uint8* freshnessValue, 
    uint32* freshnessValueLength)
{
    static uint32 txCounter = 0;
    
    if (freshnessValueId == FRESHNESS_ID_BRAKE_CMD)
    {
        txCounter++; /* Increment counter to prevent replay attacks */
        
        freshnessValue[0] = (uint8)(txCounter >> 24);
        freshnessValue[1] = (uint8)(txCounter >> 16);
        freshnessValue[2] = (uint8)(txCounter >> 8);
        freshnessValue[3] = (uint8)(txCounter);
        
        *freshnessValueLength = 32; /* 32 bits */
        return E_OK;
    }
    return E_NOT_OK;
}
```

### 2. SecOC Rx (Reception) Flow
When the ECU receives the Brake Command, it must verify the MAC before letting the Application SWC see the data.

```c
/* 
 * Callout: Verify Status 
 * SecOC calls this after checking the MAC. If it fails, we drop the frame!
 */
void SecOC_VerificationStatusCallout(
    SecOC_VerificationStatusType verificationStatus)
{
    if (verificationStatus.verificationStatus == SECOC_VERIFICATIONSUCCESS)
    {
        /* MAC is valid and Freshness is new. 
           SecOC will forward the PDU to the COM stack. */
        Dem_SetEventStatus(DemConf_DemEventParameter_SecOcFailed, DEM_EVENT_STATUS_PASSED);
    }
    else
    {
        /* MAC is invalid OR Freshness counter is old (Replay Attack) */
        
        /* 1. Report Security Violation */
        Dem_SetEventStatus(DemConf_DemEventParameter_SecOcFailed, DEM_EVENT_STATUS_FAILED);
        
        /* 2. Increment Security Event Counter for IDS (Intrusion Detection System) */
        IdsM_ReportSecurityEvent(IDSM_EVENT_SECOC_MAC_FAILURE, 1);
        
        /* SecOC automatically DROPS the PDU. 
           The Application SWC never receives the spoofed brake command. */
    }
}
```

---

## 🔐 Lab 7B: Using CSM for Secure Diagnostics (UDS 0x29)

Modern ECUs replace the weak UDS 0x27 (Seed & Key) with **UDS 0x29 (Authentication)**, which uses asymmetric cryptography (RSA/ECC) or PKI (Public Key Infrastructure).

```c
/* Dcm_Security.c */
#include "Dcm.h"
#include "Csm.h"

/* 
 * Verifying a Diagnostic Tester's Digital Signature
 * The tester sends a challenge response signed with their Private Key.
 * The ECU uses the Public Key (stored in HSM) to verify it.
 */
Std_ReturnType Dcm_VerifyTesterSignature(const uint8* signature, uint32 sigLen, const uint8* challenge, uint32 challengeLen)
{
    Csm_VerifyResultType verifyResult;
    
    /* Call Crypto Service Manager to verify RSA/ECC Signature */
    Std_ReturnType status = Csm_SignatureVerify(
        CsmConf_CsmJob_DiagnosticAuth_Verify, /* Configured Job using HSM */
        challenge, 
        challengeLen, 
        signature, 
        sigLen, 
        &verifyResult
    );

    if (status == E_OK && verifyResult == CSM_E_VERIFIED)
    {
        return E_OK; /* Tester is authenticated! Unlock flashing/coding */
    }
    
    return E_NOT_OK; /* Hacker detected */
}
```

---

## 🖥️ Simulated Attack Scenario (For the Lab)

In the practical exercise, students will use the simulation network to:
1.  **Spoofing Attack**: Try to send a raw `[0x100]` CAN frame to apply the brakes.
    *   *Result:* SecOC drops it because there is no MAC.
2.  **Replay Attack**: Record a valid SecOC brake frame and replay it 5 minutes later.
    *   *Result:* SecOC drops it because the Freshness Value (FV) counter is older than the current ECU counter.
3.  **Key Extraction Attempt**: Try to read the AES key from memory.
    *   *Result:* Fails, because the crypto driver maps to a Hardware Security Module (HSM), where keys cannot be read by the CPU, only used for calculation.
