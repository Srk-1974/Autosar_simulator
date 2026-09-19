# 🚗 AUTOSAR Training Labs: Code Templates & Solutions

This document contains the actual C and C++ source code templates that students will work on during the hands-on labs. It bridges the gap between the GUI simulator and real-world AUTOSAR development.

---

## 🛠️ Module 1 & 2: Classic Platform (SWC & OS)

### `SpeedSensor_SWC.c` (Application Software Component)
This is the implementation of the Speed Sensor SWC. It reads raw ADC values and writes the scaled speed using the RTE (Runtime Environment).

```c
#include "Rte_SpeedSensor.h"
#include "Dem.h"

#define SPEED_SCALING_FACTOR 0.244f /* Maps 0-1023 ADC to 0-250 km/h */

/* 
 * Runnable: SpeedSensor_10ms 
 * Trigger: Periodic OS Task (every 10ms)
 */
FUNC(void, RTE_CODE) SpeedSensor_10ms(void)
{
    Std_ReturnType status;
    uint16 rawAdc = 0;
    float32 speedKmh = 0.0f;

    /* 1. Read from the required port (R-PORT) */
    status = Rte_Read_AdcInputPort_AdcRawValue(&rawAdc);

    if (status == RTE_E_OK)
    {
        /* 2. Scale the raw value */
        speedKmh = (float32)rawAdc * SPEED_SCALING_FACTOR;

        /* 3. Write to the provided port (P-PORT) */
        (void)Rte_Write_SpeedOutputPort_SpeedKmh(speedKmh);

        /* Clear any previous faults */
        Dem_SetEventStatus(DemConf_DemEventParameter_SpeedSensorFault, DEM_EVENT_STATUS_PASSED);
    }
    else
    {
        /* Report a diagnostic fault if read fails */
        Dem_SetEventStatus(DemConf_DemEventParameter_SpeedSensorFault, DEM_EVENT_STATUS_FAILED);
    }
}
```

### `OS_Tasks.c` (AUTOSAR OS Implementation)
This file shows how the Runnables and Basic Software (BSW) main functions are mapped to OS tasks.

```c
#include "Os.h"
#include "Rte_Main.h"

/* BSW Headers */
#include "Com.h"
#include "NvM.h"
#include "Dcm.h"
#include "Dem.h"

/* 
 * Task: Task_10ms
 * Priority: 10
 * Schedule: FULL
 */
TASK(Task_10ms)
{
    /* Protect shared resources if necessary */
    GetResource(RES_SpeedData);

    /* Application Runnables */
    SpeedSensor_10ms();
    SpeedControl_10ms();

    /* BSW Periodic Functions */
    Com_MainFunctionTx();
    Com_MainFunctionRx();

    ReleaseResource(RES_SpeedData);
    TerminateTask();
}

/* 
 * Task: Task_100ms
 * Priority: 5 (Lower priority for background diagnostics)
 * Schedule: FULL
 */
TASK(Task_100ms)
{
    Dem_MainFunction();
    Dcm_MainFunction();
    NvM_MainFunction();
    
    TerminateTask();
}
```

---

## 🌐 Module 6: Adaptive Platform (SOME/IP ara::com)

### `SpeedService_Skeleton.cpp` (Server / Provider)
The server implementation using C++14/17 and the AUTOSAR Adaptive `ara::com` API.

```cpp
#include <iostream>
#include <thread>
#include "ara/com/sample/speed_service_skeleton.h"
#include "ara/log/logging.hpp"

using namespace ara::com::sample;

class SpeedServiceImpl : public SpeedServiceSkeleton {
private:
    ara::log::Logger& logger_;
    float current_speed_;

public:
    SpeedServiceImpl(ara::core::InstanceSpecifier const& spec)
        : SpeedServiceSkeleton(spec),
          logger_(ara::log::CreateLogger("SPDS", "Speed Service")),
          current_speed_(0.0f) {}

    /* Method Implementation: GetCurrentSpeed */
    ara::core::Future<GetCurrentSpeedOutput> GetCurrentSpeed() override {
        GetCurrentSpeedOutput output;
        output.speed_kmh = current_speed_;
        
        logger_.LogInfo() << "GetCurrentSpeed called. Returning: " << output.speed_kmh;
        
        ara::core::Promise<GetCurrentSpeedOutput> promise;
        promise.set_value(output);
        return promise.get_future();
    }

    /* Method Implementation: SetTargetSpeed */
    ara::core::Future<void> SetTargetSpeed(float target_kmh) override {
        ara::core::Promise<void> promise;

        if (target_kmh < 0.0f || target_kmh > 250.0f) {
            logger_.LogError() << "Invalid target speed requested: " << target_kmh;
            promise.SetError(ara::core::ErrorCode(SpeedServiceErrc::InvalidRange));
        } else {
            logger_.LogInfo() << "Target speed updated to: " << target_kmh;
            current_speed_ = target_kmh; /* Simplified for lab */
            promise.set_value();
        }
        return promise.get_future();
    }

    /* Event Notification Helper */
    void NotifySpeedChange() {
        // Send SOME/IP event to all subscribers
        SpeedChanged.Send(current_speed_);
    }
};

int main() {
    ara::core::Initialize();
    ara::core::InstanceSpecifier spec{"SpeedControl/SpeedService/SpeedServicePort"};
    
    SpeedServiceImpl service(spec);
    
    // Announce service on the network via SOME/IP-SD OfferService
    service.OfferService();
    std::cout << "Service Offered. Waiting for clients..." << std::endl;

    while (true) {
        service.NotifySpeedChange();
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    service.StopOfferService();
    ara::core::Deinitialize();
    return 0;
}
```

### `SpeedService_Proxy.cpp` (Client / Consumer)
The client implementation that discovers the service on the network and interacts with it.

```cpp
#include <iostream>
#include "ara/com/sample/speed_service_proxy.h"

using namespace ara::com::sample;

int main() {
    ara::core::Initialize();

    std::cout << "Starting SOME/IP-SD FindService..." << std::endl;

    // 1. Discover the service
    auto handles = SpeedServiceProxy::FindService(ara::com::InstanceIdentifier{"1"});
    
    if (handles.empty()) {
        std::cerr << "SpeedService not found on the network!" << std::endl;
        return 1;
    }

    // 2. Create Proxy
    SpeedServiceProxy proxy(handles[0]);
    std::cout << "Service found! Proxy created." << std::endl;

    // 3. Subscribe to Events
    proxy.SpeedChanged.Subscribe(5); // Queue size of 5
    proxy.SpeedChanged.SetReceiveHandler([&]() {
        proxy.SpeedChanged.GetNewSamples([](auto const& speed_sample) {
            std::cout << "[EVENT] Speed Changed: " << *speed_sample << " km/h" << std::endl;
        });
    });

    // 4. Call Method (SetTargetSpeed)
    std::cout << "Calling SetTargetSpeed(120.0)..." << std::endl;
    auto set_future = proxy.SetTargetSpeed(120.0f);
    set_future.get(); // Wait for response

    // 5. Call Method (GetCurrentSpeed)
    auto get_future = proxy.GetCurrentSpeed();
    auto result = get_future.get();
    std::cout << "[METHOD RESPONSE] Current Speed is: " << result.speed_kmh << " km/h" << std::endl;

    std::this_thread::sleep_for(std::chrono::seconds(5));

    ara::core::Deinitialize();
    return 0;
}
```
