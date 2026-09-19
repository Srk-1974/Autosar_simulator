# 🚗 AUTOSAR Engineering Mastery Course
### *From ARXML to Adaptive Platform — A Hands-On Industrial Training Program*

---

> [!IMPORTANT]
> **Critical Design Principle**: Every module culminates in a working simulation exercise.
> Students do not just read code — they configure, simulate, observe, and debug.

---

## 📐 Course Architecture at a Glance

```
Module 1 ──► Module 2 ──► Module 3 ──► Module 4 ──► Module 5 ──► Module 6
 ARXML &        OS          NvM          UDS           LIN         AUTOSAR
  SWC        Config &     Lifecycle    Diagnostics    Stack       Adaptive
Config      Scheduler                 (0x10/0x31)               (ara::com)

[Foundation] ──────────────────────────────────────────► [Advanced]
```

**Duration:** 6 Weeks (1 module/week) | 40 Hours total  
**Level:** Intermediate to Advanced Embedded Engineers  
**Prerequisites:** C programming, basic microcontroller knowledge, CAN bus fundamentals  

---

## 🗺️ Module Overview Table

| # | Module | Duration | Simulation Tool | Outcome |
|---|--------|----------|-----------------|---------|
| 1 | ARXML & SWC Configuration | 6h | DaVinci Developer / Custom ARXML Editor | Working SWC with ports & interfaces |
| 2 | OS Configuration | 6h | OSEK Simulator / Trampoline RTOS | Scheduled tasks, alarms, ISR firing |
| 3 | NvM Lifecycle | 7h | NvM Simulator / EB Tresos | Block read/write/invalidate cycle |
| 4 | UDS Diagnostics | 8h | CAPL / CANoe / UDS Simulator | Full UDS session with DTC handling |
| 5 | LIN Stack | 6h | CANoe LIN / LINalyzer | Master/Slave schedule, frame exchange |
| 6 | AUTOSAR Adaptive (SOME/IP) | 7h | COVESA SOME/IP-lib / vsomeip | Service discovery + method call |

---

---

# MODULE 1 — ARXML & SWC Port-Interface Configuration

## 🎯 Learning Objectives
After this module, students will be able to:
- [ ] Understand the AUTOSAR meta-model (M1/M2/M3 layers)
- [ ] Write and read ARXML SWC description files
- [ ] Define Port Interfaces (SenderReceiver, ClientServer)
- [ ] Configure Runnables and their triggers
- [ ] Map SWC ports to ECU composition topology

## 📚 Theory Section (2 hours)

### 1.1 AUTOSAR Layered Architecture
```
    ┌─────────────────────────────┐
    │     Application SWCs        │  ← Students work here
    ├─────────────────────────────┤
    │         RTE                 │  ← Auto-generated glue
    ├──────────┬──────────────────┤
    │ Services │  ECU Abstraction │  ← BSW
    ├──────────┴──────────────────┤
    │    MCAL (Hardware drivers)  │
    ├─────────────────────────────┤
    │    MICROCONTROLLER HW       │
    └─────────────────────────────┘
```

### 1.2 Key ARXML Elements

| ARXML Element | Purpose | Analogy |
|--------------|---------|---------|
| `PORT-INTERFACE` | Contract between SWCs | Interface/API definition |
| `P-PORT` | Provider port (sends data) | Function output |
| `R-PORT` | Receiver port (reads data) | Function input |
| `RUNNABLE` | Unit of execution | Thread/Task body |
| `DATA-ELEMENT` | Signal within an interface | Variable |
| `COMPOSITION` | Container of SWCs | System design |

### 1.3 Port Interface Types

```
SenderReceiver Interface          ClientServer Interface
┌──────────────┐                  ┌──────────────────┐
│ SWC_A        │                  │ SWC_A (Client)   │
│  P-PORT ─────┼──► data ──►      │  R-PORT ─────────┼──► Request()
│              │                  │                  │
└──────────────┘                  └──────────────────┘
┌──────────────┐                  ┌──────────────────┐
│ SWC_B        │                  │ SWC_B (Server)   │
│  R-PORT ◄────┼── data ◄──       │  P-PORT ◄────────┼── Response()
│              │                  │                  │
└──────────────┘                  └──────────────────┘
  PUSH / PULL mode                Synchronous/Async
```

## 💻 Lab 1A — Write Your First ARXML SWC (1.5 hours)

**Scenario:** Configure a `SpeedSensor_SWC` that reads raw ADC data and outputs vehicle speed.

### Step 1: Define the Port Interface
```xml
<!-- SpeedSensor_PortInterface.arxml -->
<AUTOSAR xmlns="http://autosar.org/schema/r4.0">
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>Interfaces</SHORT-NAME>
      <ELEMENTS>

        <!-- SenderReceiver Interface: ADC raw input -->
        <SENDER-RECEIVER-INTERFACE>
          <SHORT-NAME>SR_AdcRaw</SHORT-NAME>
          <DATA-ELEMENTS>
            <VARIABLE-DATA-PROTOTYPE>
              <SHORT-NAME>AdcRawValue</SHORT-NAME>
              <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">
                /AUTOSAR_Platform/ImplementationDataTypes/uint16
              </TYPE-TREF>
            </VARIABLE-DATA-PROTOTYPE>
          </DATA-ELEMENTS>
        </SENDER-RECEIVER-INTERFACE>

        <!-- SenderReceiver Interface: Speed output in km/h -->
        <SENDER-RECEIVER-INTERFACE>
          <SHORT-NAME>SR_VehicleSpeed</SHORT-NAME>
          <DATA-ELEMENTS>
            <VARIABLE-DATA-PROTOTYPE>
              <SHORT-NAME>SpeedKmh</SHORT-NAME>
              <TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">
                /AUTOSAR_Platform/ImplementationDataTypes/float32
              </TYPE-TREF>
            </VARIABLE-DATA-PROTOTYPE>
          </DATA-ELEMENTS>
        </SENDER-RECEIVER-INTERFACE>

      </ELEMENTS>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>
```

### Step 2: Define the SWC
```xml
<!-- SpeedSensor_SWC.arxml -->
<APPLICATION-SW-COMPONENT-TYPE>
  <SHORT-NAME>SpeedSensor_SWC</SHORT-NAME>

  <!-- INPUT PORT: Read raw ADC from hardware abstraction -->
  <PORTS>
    <R-PORT-PROTOTYPE>
      <SHORT-NAME>AdcInputPort</SHORT-NAME>
      <REQUIRED-INTERFACE-TREF DEST="SENDER-RECEIVER-INTERFACE">
        /Interfaces/SR_AdcRaw
      </REQUIRED-INTERFACE-TREF>
    </R-PORT-PROTOTYPE>

    <!-- OUTPUT PORT: Publish vehicle speed to other SWCs -->
    <P-PORT-PROTOTYPE>
      <SHORT-NAME>SpeedOutputPort</SHORT-NAME>
      <PROVIDED-INTERFACE-TREF DEST="SENDER-RECEIVER-INTERFACE">
        /Interfaces/SR_VehicleSpeed
      </PROVIDED-INTERFACE-TREF>
    </P-PORT-PROTOTYPE>
  </PORTS>

  <!-- INTERNAL BEHAVIOR: Runnables -->
  <INTERNAL-BEHAVIOR>
    <SHORT-NAME>SpeedSensor_IB</SHORT-NAME>
    <RUNNABLES>
      <RUNNABLE-ENTITY>
        <SHORT-NAME>SpeedSensor_10ms</SHORT-NAME>
        <!-- Triggered every 10ms by OS Task -->
        <DATA-READ-ACCESSS>
          <VARIABLE-ACCESS>
            <SHORT-NAME>Read_AdcRaw</SHORT-NAME>
            <ACCESSED-VARIABLE>
              <AUTOSAR-VARIABLE-REF>
                <PORT-PROTOTYPE-REF DEST="R-PORT-PROTOTYPE">
                  /SpeedSensor_SWC/AdcInputPort
                </PORT-PROTOTYPE-REF>
                <TARGET-DATA-PROTOTYPE-REF DEST="VARIABLE-DATA-PROTOTYPE">
                  /Interfaces/SR_AdcRaw/AdcRawValue
                </TARGET-DATA-PROTOTYPE-REF>
              </AUTOSAR-VARIABLE-REF>
            </ACCESSED-VARIABLE>
          </VARIABLE-ACCESS>
        </DATA-READ-ACCESSS>
        <DATA-SEND-POINTS>
          <VARIABLE-ACCESS>
            <SHORT-NAME>Write_Speed</SHORT-NAME>
            <ACCESSED-VARIABLE>
              <AUTOSAR-VARIABLE-REF>
                <PORT-PROTOTYPE-REF DEST="P-PORT-PROTOTYPE">
                  /SpeedSensor_SWC/SpeedOutputPort
                </PORT-PROTOTYPE-REF>
              </AUTOSAR-VARIABLE-REF>
            </ACCESSED-VARIABLE>
          </VARIABLE-ACCESS>
        </DATA-SEND-POINTS>
      </RUNNABLE-ENTITY>
    </RUNNABLES>
  </INTERNAL-BEHAVIOR>

</APPLICATION-SW-COMPONENT-TYPE>
```

## 🖥️ Simulation Exercise (2.5 hours)

**Tool:** Interactive ARXML GUI Simulator (built into this course)

**What students do:**
1. Drag & drop SWC blocks onto a canvas
2. Connect P-PORT → R-PORT visually
3. Simulator generates ARXML and C skeleton code
4. Validate port connections — errors shown in real-time
5. Inspect generated `Rte_SpeedSensor.h`

**Expected Outcome:**
```
✅ ARXML validated — no schema errors
✅ 2 ports connected: AdcInputPort (R) ← → SpeedOutputPort (P)
✅ Runnable SpeedSensor_10ms mapped to 10ms trigger
✅ RTE header generated: Rte_Read_AdcInputPort() / Rte_Write_SpeedOutputPort()
```

## ✅ Assessment — Module 1
- [ ] Add a ClientServer port for `RequestCalibration()`
- [ ] Connect a `ThrottleControl_SWC` that reads from `SpeedOutputPort`
- [ ] Validate ECU composition in simulator — no unconnected ports

---

---

# MODULE 2 — OS Configuration: Tasks, Alarms & ISR Mapping

## 🎯 Learning Objectives
- [ ] Understand OSEK/AUTOSAR OS concepts (conformance classes)
- [ ] Configure periodic tasks and event-driven tasks
- [ ] Set up alarms and counters
- [ ] Map ISRs to hardware interrupts
- [ ] Understand priority inversion and protection

## 📚 Theory Section (2 hours)

### 2.1 AUTOSAR OS Task Types

| Type | Trigger | Termination | Use Case |
|------|---------|-------------|---------|
| **Basic Task** | Activation | TerminateTask() | Short, non-blocking work |
| **Extended Task** | Activation + Event | WaitEvent() | Tasks that can block |
| **ISR Cat 1** | Hardware interrupt | Auto | Fast, no OS API calls |
| **ISR Cat 2** | Hardware interrupt | Auto | Can call OS API |

### 2.2 Task Priority & Scheduling
```
Priority 15 (Highest): ISR_CanReceive     ← Interrupt driven
Priority 10:           Task_10ms           ← SpeedSensor Runnable
Priority  8:           Task_20ms           ← ComStack Runnable  
Priority  5:           Task_100ms          ← NvM / Diagnostics
Priority  1 (Lowest):  Task_Background     ← Idle work
```

### 2.3 Alarm → Counter → Task chain
```
Hardware Timer ──► OsCounter_SystemTimer
                        │
                        ▼
                   OsAlarm_10ms ──► Activates Task_10ms every 10ms
                   OsAlarm_20ms ──► Activates Task_20ms every 20ms
                   OsAlarm_NvM  ──► Activates Task_NvM every 5ms
```

## 💻 Lab 2A — OS Configuration File (1 hour)

```c
/* ========== OS_Cfg.oil ========== */
OS ExampleOS {
    STATUS = EXTENDED;
    STARTUPHOOK = TRUE;
    ERRORHOOK = TRUE;
    PRETASKHOOK = FALSE;
    POSTTASKHOOK = FALSE;
};

/* System Timer Counter */
COUNTER SystemTimer {
    MINCYCLE = 1;
    MAXALLOWEDVALUE = 65535;
    TICKSPERBASE = 1;   /* 1 tick = 1ms */
};

/* ── Tasks ── */
TASK Task_10ms {
    PRIORITY = 10;
    ACTIVATION = 1;
    SCHEDULE = FULL;
    AUTOSTART = FALSE;
    RESOURCE = RES_SpeedData;   /* shared data protection */
};

TASK Task_100ms {
    PRIORITY = 5;
    ACTIVATION = 1;
    SCHEDULE = FULL;
    AUTOSTART = FALSE;
};

TASK Task_Background {
    PRIORITY = 1;
    ACTIVATION = 1;
    SCHEDULE = NON;
    AUTOSTART = TRUE;
};

/* ── Alarms ── */
ALARM Alarm_10ms {
    COUNTER = SystemTimer;
    ACTION = ACTIVATETASK { TASK = Task_10ms; };
    AUTOSTART = TRUE {
        APPMODE = OSDEFAULTAPPMODE;
        ALARMTIME = 1;
        CYCLETIME = 10;   /* every 10ms */
    };
};

ALARM Alarm_100ms {
    COUNTER = SystemTimer;
    ACTION = ACTIVATETASK { TASK = Task_100ms; };
    AUTOSTART = TRUE {
        ALARMTIME = 1;
        CYCLETIME = 100;
    };
};

/* ── ISR ── */
ISR ISR_CanReceive {
    CATEGORY = 2;
    PRIORITY = 15;
    SOURCE = CAN0_RX_INT;   /* hardware vector */
};

/* ── Resources (for priority ceiling) ── */
RESOURCE RES_SpeedData {
    RESOURCEPROPERTY = STANDARD;
};
```

## 💻 Lab 2B — Task Implementation
```c
/* Task_10ms body — runs every 10ms */
TASK(Task_10ms)
{
    GetResource(RES_SpeedData);

    /* Call SWC runnables mapped to 10ms */
    SpeedSensor_10ms();       /* Runnable from Module 1 SWC */
    SpeedControl_10ms();
    Com_MainFunctionTx();     /* CAN transmission cycle */

    ReleaseResource(RES_SpeedData);
    TerminateTask();
}

TASK(Task_100ms)
{
    Dcm_MainFunction();       /* UDS diagnostics tick */
    Dem_MainFunction();       /* DEM event processing */
    NvM_MainFunction();       /* NvM background processing */
    TerminateTask();
}

ISR(ISR_CanReceive)
{
    Can_IsrRx_0();            /* CAN driver ISR handler */
}
```

## 🖥️ Simulation Exercise — OS Task Scheduler Visualizer (2.5 hours)

**Tool:** Interactive AUTOSAR OS Simulator (in course GUI tool)

**What students observe:**
- Live Gantt chart of task execution timeline
- Priority preemption shown visually
- Alarm firing events highlighted
- CPU load percentage per task
- Deadline miss detection

**Simulation Scenarios:**
1. Normal operation: all tasks meeting deadlines
2. **Overload scenario**: Task_10ms takes >10ms — student observes deadline miss
3. **Priority inversion**: Two tasks sharing resource — deadlock demonstration
4. ISR latency measurement

---

---

# MODULE 3 — NvM: EEPROM Block Lifecycle

## 🎯 Learning Objectives
- [ ] Understand NvM block types (Native, Redundant, Dataset)
- [ ] Implement read-all / write-all startup/shutdown sequences
- [ ] Handle job result callbacks and error status
- [ ] Configure MemIf, Fee (Flash), and Ea (EEPROM) layers

## 📚 Theory (1.5 hours)

### 3.1 NvM Memory Stack Architecture
```
Application / BSW Modules
        │  NvM_ReadBlock()  NvM_WriteBlock()
        ▼
┌───────────────────────┐
│  NvM (AUTOSAR R4.x)   │  ← Queue, job scheduler
├───────────┬───────────┤
│   MemIf   │           │  ← Abstract layer
├───────────┤           │
│ Fee (Flash)│ Ea (EE)  │  ← Medium-specific
├───────────┴───────────┤
│  Fls / Eep (MCAL)     │  ← Hardware driver
├───────────────────────┤
│  Flash / EEPROM HW    │
└───────────────────────┘
```

### 3.2 NvM Block Types

| Type | Copies | Use Case | Overhead |
|------|--------|---------|---------|
| **NATIVE** | 1 | General data storage | Low |
| **REDUNDANT** | 2 | Safety-critical data | 2x storage |
| **DATASET** | N | Calibration sets (multi-instance) | N×storage |

### 3.3 Read/Write Lifecycle State Machine
```
ECU STARTUP:                    ECU SHUTDOWN:
                                
NvM_ReadAll()                   NvM_WriteAll()
     │                               │
     ▼                               ▼
[Reading blocks]              [Writing dirty blocks]
     │                               │
     ▼                               ▼
NvM_GetErrorStatus()          NvM_GetErrorStatus()
== NVM_REQ_OK                 == NVM_REQ_OK
     │                               │
     ▼                               ▼
  App starts                    EcuM shutdown
```

## 💻 Lab 3A — NvM Block Configuration
```c
/* NvM_Cfg.h — Block descriptor (normally generated by tool) */

/* Block 1: Target Speed (safety-relevant → REDUNDANT) */
#define NvMConf_NvMBlockDescriptor_TargetSpeed      ((NvM_BlockIdType)1U)
/* Block 2: Odometer value */
#define NvMConf_NvMBlockDescriptor_Odometer         ((NvM_BlockIdType)2U)
/* Block 3: Fault memory (DEM mirror) */
#define NvMConf_NvMBlockDescriptor_DemNvData        ((NvM_BlockIdType)3U)

/* ───────────────────────────────────── */
/* Runtime read example                  */
/* ───────────────────────────────────── */
#define TARGETSPEED_BLOCK_SIZE  (4U)  /* float32 = 4 bytes */

static float32 TargetSpeed_RamBuffer = 0.0f;

void App_ReadTargetSpeedFromNvM(void)
{
    NvM_RequestResultType result;

    /* Asynchronous read — returns immediately */
    (void)NvM_ReadBlock(NvMConf_NvMBlockDescriptor_TargetSpeed,
                        &TargetSpeed_RamBuffer);

    /* Poll for completion (in production: use callback) */
    do {
        NvM_MainFunction();  /* drives the NvM state machine */
        NvM_GetErrorStatus(NvMConf_NvMBlockDescriptor_TargetSpeed, &result);
    } while (result == NVM_REQ_PENDING);

    if (result == NVM_REQ_OK)
    {
        /* TargetSpeed_RamBuffer now has valid data from flash */
        SpeedControl_SetTargetSpeed(TargetSpeed_RamBuffer);
    }
    else if (result == NVM_REQ_NV_INVALIDATED)
    {
        /* First boot — use default value */
        TargetSpeed_RamBuffer = 80.0f;  /* 80 km/h default */
        SpeedControl_SetTargetSpeed(TargetSpeed_RamBuffer);
    }
}

void App_WriteTargetSpeedToNvM(float32 newSpeed)
{
    TargetSpeed_RamBuffer = newSpeed;

    /* Write back — NvM copies from RAM buffer to Flash */
    (void)NvM_WriteBlock(NvMConf_NvMBlockDescriptor_TargetSpeed,
                         &TargetSpeed_RamBuffer);
}
```

## 🖥️ Simulation Exercise — NvM Block Lifecycle Simulator (3 hours)

**What students do:**
1. Configure 3 NvM blocks (Native, Redundant, Dataset)
2. Simulate ECU startup → `ReadAll` sequence — watch blocks load
3. Modify a value and trigger `WriteBlock`
4. Simulate **power loss** mid-write — observe redundant block recovery
5. Invalidate a block and observe default value restoration
6. Measure write latency in simulation cycles

**Expected outcomes to observe:**
```
[STARTUP]  NvM_ReadAll started — 3 blocks queued
[BLOCK 1]  TargetSpeed read OK (80.0 km/h)
[BLOCK 2]  Odometer read OK (52341 km)
[BLOCK 3]  DemNvData: NVM_REQ_NV_INVALIDATED → defaults applied
[MODIFY]   TargetSpeed set to 100.0 km/h
[WRITE]    NvM_WriteBlock queued for Block 1
[COMPLETE] Write confirmed — Flash updated
[POWER CUT] Simulated! → Redundant copy used for recovery ✅
```

---

---

# MODULE 4 — UDS Diagnostics: Sessions & Routine Control

## 🎯 Learning Objectives
- [ ] Understand ISO 14229-1 UDS protocol structure
- [ ] Implement session management (0x10)
- [ ] Configure security access (0x27 seed/key)
- [ ] Read/Write DIDs (0x22, 0x2E)
- [ ] Execute ECU routines (0x31)
- [ ] Handle DTC reading (0x19) and clearing (0x14)

## 📚 Theory (2 hours)

### 4.1 UDS Session Hierarchy
```
DEFAULT SESSION (0x01) — Always active
    │
    ├── Read DTCs (0x19)
    ├── Read Data (0x22) — non-secured DIDs
    └── ECU Reset (0x11)

EXTENDED DIAGNOSTIC SESSION (0x03)
    │
    ├── All Default services +
    ├── Write Data (0x2E) — some DIDs
    └── Communication Control (0x28)

PROGRAMMING SESSION (0x02)
    │  [Requires Security Access 0x27 first]
    │
    ├── Download/Upload (0x34, 0x35, 0x36, 0x37)
    ├── Write Data (0x2E) — all DIDs
    └── Routine Control (0x31)
```

### 4.2 UDS Frame Structure on CAN
```
CAN ID: 0x7DF (Physical)  or  0x7E0-0x7E7 (Functional)
       ┌────┬────┬────┬────┬────┬────┬────┬────┐
Byte:  │ 0  │ 1  │ 2  │ 3  │ 4  │ 5  │ 6  │ 7  │
       ├────┼────┼────┼────┼────┼────┼────┼────┤
Data:  │PCI │ SID│ DID│ DID│Data│Data│ FF │ FF │
       └────┴────┴────┴────┴────┴────┴────┴────┘
        │    │    └─── Service parameter
        │    └──────── Service ID (0x22 = ReadDID)
        └───────────── Protocol Control Info (SF=0x02 for 2 more bytes)
```

### 4.3 Routine Control (0x31) sub-functions

| Sub-function | Code | Action |
|-------------|------|--------|
| startRoutine | 0x01 | Start the routine |
| stopRoutine | 0x02 | Stop a running routine |
| requestRoutineResults | 0x03 | Read result of last execution |

## 💻 Lab 4A — Full UDS Session Simulation

### Request: Start Extended Session
```
→ TX: 02 10 03 FF FF FF FF FF   (StartDiagnosticSession = Extended)
← RX: 02 50 03 00 19 01 F4 FF   (PositiveResponse, P2=25ms, P2*=500ms)
```

### Request: Security Access (Seed Request)
```
→ TX: 02 27 01 FF FF FF FF FF   (RequestSeed, Level 0x01)
← RX: 06 67 01 DE AD BE EF FF   (Seed = 0xDEADBEEF)
```

### Request: Security Access (Key Send)
```
Tester calculates: Key = Seed XOR 0xC0FFEE42 = 0x1E537CAD
→ TX: 06 27 02 1E 53 7C AD FF
← RX: 02 67 02 FF FF FF FF FF   (Access granted ✅)
```

### Request: Write DID 0x2001 — Target Speed = 120 km/h
```
Target = 120.0 km/h → scaled × 10 = 1200 = 0x04B0
→ TX: 05 2E 20 01 04 B0 FF FF
← RX: 03 6E 20 01 FF FF FF FF   (WriteDataByIdentifier positive response)
```

### Request: Routine Control — Run Self-Test (Routine 0x0100)
```
→ TX: 04 31 01 01 00 FF FF FF   (startRoutine 0x0100)
← RX: 04 71 01 01 00 FF FF FF   (Routine started)

→ TX: 04 31 03 01 00 FF FF FF   (requestRoutineResults)
← RX: 05 71 03 01 00 00 FF FF   (Result: 0x00 = PASS ✅)
```

## 💻 Lab 4B — DCM Callout Implementation
```c
/* Routine 0x0100: Run speed sensor self-test */
Std_ReturnType Dcm_RoutineControl_SpeedSensorTest(
    Dcm_OpStatusType    opStatus,
    uint8               routineOption,
    P2VAR(uint8, AUTOMATIC, DCM_VAR) routineStatusRecord,
    P2VAR(uint16, AUTOMATIC, DCM_VAR) routineStatusRecordLength,
    P2VAR(Dcm_NegativeResponseCodeType, AUTOMATIC, DCM_VAR) errorCode)
{
    static uint8 testResult = 0xFFU;

    switch (opStatus)
    {
        case DCM_INITIAL:
            /* Start async self-test */
            SpeedSensor_StartSelfTest();
            return DCM_E_PENDING;  /* tell DCM to call again */

        case DCM_PENDING:
            if (SpeedSensor_IsSelfTestComplete())
            {
                testResult = SpeedSensor_GetSelfTestResult();
                routineStatusRecord[0] = testResult;
                *routineStatusRecordLength = 1U;
                return E_OK;
            }
            return DCM_E_PENDING;

        case DCM_CANCEL:
            SpeedSensor_AbortSelfTest();
            return E_OK;

        default:
            *errorCode = DCM_E_CONDITIONSNOTCORRECT;
            return E_NOT_OK;
    }
}
```

## 🖥️ Simulation Exercise — UDS Interactive Console (3 hours)

**What students do in the GUI simulator:**
1. Connect a "virtual tester" to a simulated ECU
2. Type UDS requests in hex — observe real-time response
3. Walk through session escalation: Default → Extended → Programming
4. Trigger security access with correct and incorrect keys (observe lockout)
5. Write a DID and read it back
6. Inject a fault, read DTC via 0x19, clear via 0x14
7. Execute and query a routine with PASS/FAIL results

---

---

# MODULE 5 — LIN Stack: Master/Slave Communication

## 🎯 Learning Objectives
- [ ] Understand LIN protocol (break, sync, PID, data, checksum)
- [ ] Configure Master schedule table
- [ ] Configure Slave response
- [ ] Map LIN frames to AUTOSAR signals
- [ ] Handle LIN error detection (checksum, timeout, no-response)

## 📚 Theory (1.5 hours)

### 5.1 LIN Frame Structure
```
  ┌────────────┬──────┬───────────┬──────────────┬──────────┐
  │ BREAK      │ SYNC │  PID      │  DATA[0..7]  │ CHECKSUM │
  │ (13 bits 0)│ 0x55 │  6+P0+P1  │  1-8 bytes   │  1 byte  │
  └────────────┴──────┴───────────┴──────────────┴──────────┘

PID = Frame ID (6 bits) + Parity (2 bits)
Frame ID 0x00-0x3B: Signal frames
Frame ID 0x3C:      Master request (diagnostic)
Frame ID 0x3D:      Slave response (diagnostic)
```

### 5.2 LIN vs CAN Comparison

| Feature | LIN | CAN |
|---------|-----|-----|
| Speed | 20 kbit/s | 500 kbit/s – 1 Mbit/s |
| Topology | Single-wire bus | Differential pair |
| Arbitration | Schedule-based (master-controlled) | CSMA/CD |
| Cost | Very low | Higher |
| Use case | Window motors, HVAC, seats | Powertrain, safety |
| Nodes | 1 master + up to 16 slaves | Up to 32+ nodes |

### 5.3 AUTOSAR LIN Stack Architecture
```
Application SWC
     │
     ▼ Rte_Write / Rte_Read
    COM (signals)
     │
     ▼
    LinIf  ←── Schedule Table Management
     │
     ▼
    LinTp  (for diagnostic frames 0x3C/0x3D)
     │
     ▼
    Lin MCAL (hardware UART/LIN driver)
     │
     ▼
    LIN Bus Hardware
```

## 💻 Lab 5A — LIN Schedule Table Configuration
```xml
<!-- LIN Schedule Table: Window Control -->
<LIN-SCHEDULE-TABLE>
  <SHORT-NAME>WindowControl_Schedule</SHORT-NAME>
  <SCHEDULE-TABLE-ENTRIES>

    <!-- Frame 0x01: Window Position (every 20ms) -->
    <SCHEDULE-TABLE-ENTRY>
      <FRAME-REF DEST="LIN-FRAME">/LinFrames/WindowPosition</FRAME-REF>
      <DELAY>20</DELAY>  <!-- ms -->
    </SCHEDULE-TABLE-ENTRY>

    <!-- Frame 0x02: Switch Status (every 20ms) -->
    <SCHEDULE-TABLE-ENTRY>
      <FRAME-REF DEST="LIN-FRAME">/LinFrames/SwitchStatus</FRAME-REF>
      <DELAY>20</DELAY>
    </SCHEDULE-TABLE-ENTRY>

    <!-- Frame 0x03: Motor Temperature (every 100ms) -->
    <SCHEDULE-TABLE-ENTRY>
      <FRAME-REF DEST="LIN-FRAME">/LinFrames/MotorTemp</FRAME-REF>
      <DELAY>100</DELAY>
    </SCHEDULE-TABLE-ENTRY>

  </SCHEDULE-TABLE-ENTRIES>
</LIN-SCHEDULE-TABLE>
```

## 💻 Lab 5B — LIN Slave Node Implementation
```c
/* LinIf_SlaveWindowMotor.c */
#include "LinIf.h"

/* Frame 0x01 response buffer — Window Position 0-100% */
static uint8 WindowPos_Response[2] = { 0x00U, 0x00U };

void LinIf_SlaveWakeupNotification(NetworkHandleType channel)
{
    Lin_GoToNormalMode(channel);
}

/* Called by LinIf when master requests Frame ID 0x01 */
Std_ReturnType LinIf_HeaderIndication(
    NetworkHandleType  channel,
    P2VAR(Lin_PduType, AUTOMATIC, LINIF_APPL_VAR) pdu)
{
    if (pdu->Pid == 0x01U)  /* Window Position frame */
    {
        /* Read ADC position sensor → convert to % */
        uint16 adcVal;
        Adc_ReadGroup(ADC_GROUP_WINDOW, &adcVal);

        uint8 posPercent = (uint8)((adcVal * 100U) / 1023U);
        WindowPos_Response[0] = posPercent;
        WindowPos_Response[1] = 0x00U;   /* reserved */

        pdu->SduPtr  = WindowPos_Response;
        pdu->Dl      = 2U;
        pdu->Cs      = LIN_ENHANCED_CS;
        pdu->Drc     = LIN_SLAVE_RESPONSE;

        return E_OK;
    }
    return E_NOT_OK;
}
```

## 🖥️ Simulation Exercise — LIN Bus Analyzer (2.5 hours)

**What students observe:**
- Real-time LIN frame transmission on virtual bus
- Schedule table cycling through frames
- Signal values updating with each frame
- Checksum error injection — observe slave no-response
- Bus timeout detection and LIN error status

---

---

# MODULE 6 — AUTOSAR Adaptive Platform: ara::com & SOME/IP

## 🎯 Learning Objectives
- [ ] Understand Adaptive Platform architecture vs Classic
- [ ] Implement a SOME/IP service with ara::com
- [ ] Configure service discovery (SD)
- [ ] Invoke remote methods (request/response)
- [ ] Use events (pub/sub) and fields
- [ ] Write manifest files (JSON service description)

## 📚 Theory (2 hours)

### 6.1 Classic vs Adaptive Architecture

| Aspect | Classic Platform | Adaptive Platform |
|--------|-----------------|-------------------|
| OS | AUTOSAR OS (OSEK) | POSIX (Linux/QNX) |
| Communication | Signal-based COM | Service-based ara::com |
| Protocol | CAN/LIN/FlexRay | Ethernet (SOME/IP) |
| Updates | Flash reprogramming | OTA possible |
| Language | C | C++14/17 |
| Use case | Powertrain, Chassis | Infotainment, ADAS, V2X |

### 6.2 SOME/IP Message Types

| Type | Direction | Use Case |
|------|-----------|---------|
| **Request** | Client → Server | Remote method call |
| **Response** | Server → Client | Method return value |
| **Notification** | Server → Client | Periodic/event data |
| **SD Offer** | Server → Network | "I provide this service" |
| **SD Find** | Client → Network | "Who provides this?" |
| **SD Subscribe** | Client → Server | Event subscription |

### 6.3 ara::com API Structure
```cpp
// Server side
auto speedService = ara::com::ServiceInterface<SpeedService>::Create();
speedService->OfferService();

// Client side
auto proxy = SpeedServiceProxy::StartFindService(...);
proxy->GetSpeed.Get();           // Method call
proxy->SpeedChanged.Subscribe(); // Event subscription
```

## 💻 Lab 6A — Service Manifest File
```json
{
  "serviceInterface": {
    "shortName": "SpeedService",
    "serviceId": 1001,
    "majorVersion": 1,
    "minorVersion": 0,
    "methods": [
      {
        "shortName": "GetCurrentSpeed",
        "methodId": 1,
        "fireAndForget": false,
        "inputParameters": [],
        "outputParameters": [
          { "name": "speed_kmh", "dataType": "float32" }
        ]
      },
      {
        "shortName": "SetTargetSpeed",
        "methodId": 2,
        "fireAndForget": false,
        "inputParameters": [
          { "name": "target_kmh", "dataType": "float32" }
        ],
        "outputParameters": []
      }
    ],
    "events": [
      {
        "shortName": "SpeedChanged",
        "eventId": 1,
        "dataType": "float32",
        "cycleTime": 100
      }
    ],
    "fields": [
      {
        "shortName": "MaxSpeed",
        "fieldId": 1,
        "dataType": "float32",
        "hasGetter": true,
        "hasSetter": true
      }
    ]
  }
}
```

## 💻 Lab 6B — ara::com Service Implementation (C++17)

### Server (Skeleton)
```cpp
// SpeedService_Skeleton.cpp
#include "ara/com/sample/speed_service_skeleton.h"
#include "ara/log/logging.hpp"

class SpeedServiceImpl : public SpeedServiceSkeleton
{
public:
    explicit SpeedServiceImpl(ara::core::InstanceSpecifier const& spec)
        : SpeedServiceSkeleton(spec)
        , logger_(ara::log::CreateLogger("SPDS", "Speed Service"))
    {}

    /* Method: GetCurrentSpeed */
    ara::core::Future<GetCurrentSpeedOutput> GetCurrentSpeed() override
    {
        GetCurrentSpeedOutput output;
        output.speed_kmh = ReadSpeedSensor();   /* HAL call */

        logger_.LogInfo() << "GetCurrentSpeed: " << output.speed_kmh;

        ara::core::Promise<GetCurrentSpeedOutput> promise;
        promise.set_value(output);
        return promise.get_future();
    }

    /* Method: SetTargetSpeed */
    ara::core::Future<void> SetTargetSpeed(float target_kmh) override
    {
        if (target_kmh < 0.0f || target_kmh > 200.0f)
        {
            ara::core::Promise<void> p;
            p.SetError(ara::core::ErrorCode(SpeedServiceErrc::InvalidRange));
            return p.get_future();
        }
        SpeedControl_SetTarget(target_kmh);

        ara::core::Promise<void> p;
        p.set_value();
        return p.get_future();
    }

    /* Periodic event sender — called every 100ms */
    void SendSpeedEvent()
    {
        float current = ReadSpeedSensor();
        SpeedChanged.Send(current);  /* notify all subscribers */
    }

private:
    ara::log::Logger& logger_;
};

int main()
{
    ara::core::Initialize();
    ara::core::InstanceSpecifier spec{"SpeedControl/SpeedService/SpeedServicePort"};
    SpeedServiceImpl service(spec);
    service.OfferService();

    while (true)
    {
        service.SendSpeedEvent();
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    service.StopOfferService();
    ara::core::Deinitialize();
    return 0;
}
```

### Client (Proxy)
```cpp
// SpeedClient.cpp
#include "ara/com/sample/speed_service_proxy.h"

using namespace ara::com::sample;

int main()
{
    ara::core::Initialize();

    /* Find the service via SOME/IP Service Discovery */
    auto handles = SpeedServiceProxy::FindService(
        ara::com::InstanceIdentifier{"1"});

    if (handles.empty()) {
        std::cerr << "Service not found!\n";
        return 1;
    }

    SpeedServiceProxy proxy(handles[0]);

    /* Subscribe to SpeedChanged event */
    proxy.SpeedChanged.Subscribe(5);  /* queue size = 5 */
    proxy.SpeedChanged.SetReceiveHandler([&]() {
        auto samples = proxy.SpeedChanged.GetNewSamples(
            [](auto& speed) {
                std::cout << "Speed update: " << *speed << " km/h\n";
            });
    });

    /* Call GetCurrentSpeed method */
    auto future = proxy.GetCurrentSpeed();
    auto result = future.get();
    std::cout << "Current speed: " << result.speed_kmh << " km/h\n";

    /* Set target speed */
    proxy.SetTargetSpeed(120.0f).get();
    std::cout << "Target set to 120 km/h\n";

    ara::core::Deinitialize();
    return 0;
}
```

## 🖥️ Simulation Exercise — SOME/IP Service Discovery Simulator (3 hours)

**What students see:**
1. Two virtual ECUs on an Ethernet network
2. Server announces service via SD Offer message
3. Client discovers service — SD Find/Offer exchange shown
4. Method call sequence: Request → Response (Wireshark-style view)
5. Event subscription and periodic notifications
6. Network disconnect simulation — service re-discovery

---

---

# 🛠️ Tool Stack & Lab Environment

## Recommended Tools Per Module

| Module | Free/Open-Source | Commercial |
|--------|-----------------|-----------|
| ARXML (M1) | Eclipse AASX, Papyrus-AUTOSAR | Vector DaVinci Developer |
| OS (M2) | Trampoline RTOS, FreeOSEK | ETAS RTA-OS, EB Tresos |
| NvM (M3) | Custom simulator (this course) | EB Tresos NvM plugin |
| UDS (M4) | python-udsoncan, CAPL-lite | Vector CANoe + CAPL |
| LIN (M5) | LINalyzer (free), python-lin | Vector CANoe LIN |
| Adaptive (M6) | vsomeip (COVESA), ara::com mock | ETAS VRTE |

## 🎮 This Course's Custom GUI Simulator Covers:
- ✅ ARXML port connection visualizer
- ✅ OS Task Gantt chart / scheduler
- ✅ NvM block read/write lifecycle
- ✅ UDS interactive console (hex input/output)
- ✅ LIN frame bus analyzer
- ✅ SOME/IP service discovery flow

---

# 📊 Assessment & Grading

| Assessment | Weight | Description |
|-----------|--------|-------------|
| Lab completion (per module) | 30% | Simulator exercises completed |
| Module quizzes | 20% | 10 questions per module |
| Midterm project | 20% | Full SWC + OS integration |
| Final project | 30% | End-to-end ECU simulation |

## 🏁 Final Project
**Build a fully simulated "Speed Control ECU"** covering:
1. ARXML SWC with 4 ports
2. OS: 3 tasks + 2 alarms + 1 ISR
3. NvM: 2 blocks (target speed + odometer)
4. UDS: Read speed DID + self-test routine
5. LIN: Window motor control (bonus)
6. Adaptive: REST/SOME/IP speed reporting (bonus)

---

# 🗓️ Course Schedule

| Week | Module | Lab Focus |
|------|--------|-----------|
| 1 | ARXML & SWC | Port connection, runnable mapping |
| 2 | OS Configuration | Task scheduling, Gantt analysis |
| 3 | NvM Lifecycle | Power-cut recovery, redundant blocks |
| 4 | UDS Diagnostics | Full session flow, DTC management |
| 5 | LIN Stack | Schedule table, frame analysis |
| 6 | Adaptive / SOME/IP | Service discovery, client-server demo |

---

> [!TIP]
> **Instructor Tip**: Run Module 2 (OS) immediately after Module 1 (ARXML) — students
> can map their SWC runnables to tasks they configure in Module 2. This cross-module
> connection is highly motivating and reinforces both concepts simultaneously.
