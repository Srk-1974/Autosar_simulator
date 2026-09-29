import os

session_html = """
  <!-- ── LEARNING SESSION TAB ── -->
  <div id="tab-session" class="hidden">
    <div class="flex items-center justify-between mb-4 bg-[var(--card)] p-3 rounded-lg border border-[var(--border)] fade-up">
      <button onclick="showTab('modules')" class="text-xs font-bold text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition">← Back to Dashboard</button>
      <h2 id="session-title" class="text-sm font-bold text-[var(--primary)]">Module Title</h2>
      <a href="autosar_simulator.html" target="_blank" class="bg-green-500/10 text-green-500 border border-green-500/50 text-xs px-3 py-1.5 rounded font-bold hover:bg-green-500/20 transition">🚀 Launch Simulator</a>
    </div>
    <div class="bg-[var(--card)] border border-[var(--border)] rounded-lg p-6 fade-up fade-up-1">
      <div id="session-content" class="space-y-4 text-sm leading-relaxed">
        <!-- Content injected via JS -->
      </div>
    </div>
  </div>
"""

session_data_js = """
const sessionData = {
  0: `
    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">1. The AUTOSAR Meta-Model & SWCs</h3>
    <p class="text-[var(--muted-foreground)] mb-4">In AUTOSAR, the Application Layer is composed of Software Components (SWCs). These components are independent of the hardware and communicate with each other using the Runtime Environment (RTE). The configuration of these SWCs, their ports, and interfaces is defined using ARXML (AUTOSAR XML).</p>
    
    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">2. Sender-Receiver Interfaces</h3>
    <p class="text-[var(--muted-foreground)] mb-4">A Sender-Receiver interface is used for passing data (like vehicle speed or temperature). A <strong>P-PORT</strong> (Provider) sends the data, and an <strong>R-PORT</strong> (Receiver) reads it.</p>
    
    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">3. Example C Code (SpeedSensor_SWC.c)</h3>
    <pre class="bg-[#0f172a] text-gray-300 p-4 rounded-lg font-mono text-xs overflow-x-auto mb-4 border border-[var(--border)]"><code>#include "Rte_SpeedSensor.h"

FUNC(void, RTE_CODE) SpeedSensor_10ms(void) {
    uint16 rawAdc = 0;
    float32 speedKmh = 0.0f;
    
    /* Read from R-PORT */
    if (Rte_Read_AdcInputPort_AdcRawValue(&rawAdc) == RTE_E_OK) {
        speedKmh = (float32)rawAdc * 0.244f;
        
        /* Write to P-PORT */
        Rte_Write_SpeedOutputPort_SpeedKmh(speedKmh);
    }
}</code></pre>
    
    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">🧪 Lab Instructions</h3>
    <div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
        <ul class="list-disc pl-5 text-[var(--muted-foreground)] space-y-1">
            <li>Click <strong>Launch Simulator</strong> at the top right of this page.</li>
            <li>Go to the <strong>M1: ARXML & SWC</strong> tab.</li>
            <li>Click <strong>Connect Ports</strong> to link the Provider and Receiver ports together.</li>
            <li>Click <strong>Validate ARXML</strong> to generate the RTE header automatically!</li>
        </ul>
    </div>
  `,
  1: `
    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">1. AUTOSAR OS & OSEK Concepts</h3>
    <p class="text-[var(--muted-foreground)] mb-4">AUTOSAR OS is a statically configured real-time operating system based on the OSEK/VDX standard. It uses priority-based preemptive scheduling to guarantee that high-priority tasks meet their strict timing deadlines.</p>
    
    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">2. Task Types & Mapping</h3>
    <p class="text-[var(--muted-foreground)] mb-4">Runnables from SWCs (like our 10ms SpeedSensor runnable) must be mapped to OS Tasks. <strong>Basic Tasks</strong> run to completion, while <strong>Extended Tasks</strong> can block waiting for events. <strong>ISRs</strong> (Interrupt Service Routines) preempt all tasks.</p>
    
    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">3. Example C Code (OS_Tasks.c)</h3>
    <pre class="bg-[#0f172a] text-gray-300 p-4 rounded-lg font-mono text-xs overflow-x-auto mb-4 border border-[var(--border)]"><code>#include "Os.h"

TASK(Task_10ms) {
    GetResource(RES_SpeedData); /* Priority Ceiling Protocol */
    
    SpeedSensor_10ms(); /* Application Runnable */
    Com_MainFunctionTx(); /* BSW Runnable */
    
    ReleaseResource(RES_SpeedData);
    TerminateTask();
}</code></pre>

    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">🧪 Lab Instructions</h3>
    <div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
        <ul class="list-disc pl-5 text-[var(--muted-foreground)] space-y-1">
            <li>Launch the Simulator and go to <strong>M2: OS Scheduler</strong>.</li>
            <li>Press <strong>Start</strong> to watch the tasks preempt each other on the live Gantt chart.</li>
            <li>Click <strong>Inject Overload</strong> to simulate a task running too long, and observe the resulting ❌ Deadline Miss error!</li>
        </ul>
    </div>
  `,
  2: `
    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">1. Non-Volatile Memory (NvM) Lifecycle</h3>
    <p class="text-[var(--muted-foreground)] mb-4">The NvM stack manages reading and writing data to Flash or EEPROM. To preserve flash life and ensure performance, NvM uses RAM mirrors. Data is loaded during ECU Startup (<code>NvM_ReadAll</code>) and written back during ECU Shutdown (<code>NvM_WriteAll</code>).</p>
    
    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">2. Redundancy & Reliability</h3>
    <p class="text-[var(--muted-foreground)] mb-4">Critical data (like odometers or immobilizer keys) use <strong>REDUNDANT</strong> block types. The NvM stores two copies. If power is lost mid-write and copy A is corrupted, copy B is used to recover the data on the next boot.</p>
    
    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">🧪 Lab Instructions</h3>
    <div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
        <ul class="list-disc pl-5 text-[var(--muted-foreground)] space-y-1">
            <li>Launch the Simulator and go to <strong>M3: NvM Lifecycle</strong>.</li>
            <li>Click <strong>NvM_ReadAll</strong> to simulate the ECU booting up.</li>
            <li>Click <strong>Write Block 1</strong>, and then quickly click <strong>Simulate Power Cut</strong> while it's writing to watch the Redundant block auto-recover the corrupted data!</li>
        </ul>
    </div>
  `,
  3: `
    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">1. UDS Diagnostics (ISO 14229)</h3>
    <p class="text-[var(--muted-foreground)] mb-4">Unified Diagnostic Services (UDS) allows external testers to read ECU data, write configuration, and trigger routines. The DCM (Diagnostic Communication Manager) handles these requests.</p>

    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">2. Sessions and Security</h3>
    <p class="text-[var(--muted-foreground)] mb-4">By default, an ECU is in the <code>Default Session (0x01)</code>. To write sensitive data, you must enter an <code>Extended Session (0x03)</code> and unlock the ECU using <code>Security Access (0x27)</code>.</p>

    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">3. UDS Request Structure</h3>
    <pre class="bg-[#0f172a] text-gray-300 p-4 rounded-lg font-mono text-xs overflow-x-auto mb-4 border border-[var(--border)]"><code>TX: 02 27 01 FF FF FF FF FF
  02 = Protocol Control Info (Length: 2 bytes)
  27 = Service ID (Security Access)
  01 = Sub-function (Request Seed)</code></pre>

    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">🧪 Lab Instructions</h3>
    <div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
        <ul class="list-disc pl-5 text-[var(--muted-foreground)] space-y-1">
            <li>Launch the Simulator and go to <strong>M4: UDS Diagnostics</strong>.</li>
            <li>Attempt to <strong>Write Speed</strong> (0x2E). Notice it fails (NRC 0x33: Security Access Denied).</li>
            <li>Escalate your session (0x10), request a seed (0x27 01), and send the key (0x27 02) to unlock the ECU, then try writing the speed again!</li>
        </ul>
    </div>
  `,
  4: `
    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">1. LIN Bus Fundamentals</h3>
    <p class="text-[var(--muted-foreground)] mb-4">LIN (Local Interconnect Network) is a low-cost, single-wire serial bus. Unlike CAN, it relies on a strict <strong>Master-Slave</strong> architecture. Only the Master can initiate communication by sending a frame header.</p>

    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">2. The Schedule Table</h3>
    <p class="text-[var(--muted-foreground)] mb-4">The Master uses a Schedule Table to decide which frame header to send and when. For example, it might ask for Window Position every 20ms, and Motor Temp every 100ms. Slaves must wait for their specific PID to respond.</p>

    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">🧪 Lab Instructions</h3>
    <div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
        <ul class="list-disc pl-5 text-[var(--muted-foreground)] space-y-1">
            <li>Launch the Simulator and go to <strong>M5: LIN Stack</strong>.</li>
            <li>Click <strong>Start LIN Scheduler</strong> to observe the Master cycling through the schedule table.</li>
            <li>Inject a <strong>Checksum Error</strong> and watch how the Master detects a Slave failure and reports it via the AUTOSAR DET/DEM.</li>
        </ul>
    </div>
  `,
  5: `
    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">1. AUTOSAR Adaptive & SOME/IP</h3>
    <p class="text-[var(--muted-foreground)] mb-4">The Adaptive Platform is designed for high-performance computing (ADAS, Infotainment). It uses C++14/17 and a POSIX OS (like Linux). Communication is Service-Oriented (ara::com) over Ethernet using SOME/IP.</p>

    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">2. Service Discovery (SD)</h3>
    <p class="text-[var(--muted-foreground)] mb-4">ECUs don't broadcast raw signals blindly anymore. A Server multicasts an <code>OfferService</code> packet. A Client replies with <code>FindService</code> and <code>SubscribeEvent</code> to start communicating.</p>

    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">3. Example C++ Code (Server Skeleton)</h3>
    <pre class="bg-[#0f172a] text-gray-300 p-4 rounded-lg font-mono text-xs overflow-x-auto mb-4 border border-[var(--border)]"><code>#include "ara/com/sample/speed_service_skeleton.h"

class SpeedServiceImpl : public SpeedServiceSkeleton {
public:
    ara::core::Future<void> SetTargetSpeed(float target_kmh) override {
        /* Handle RPC call */
        ara::core::Promise<void> promise;
        promise.set_value();
        return promise.get_future();
    }
};

int main() {
    SpeedServiceImpl service(spec);
    service.OfferService(); /* Announce to network */
}</code></pre>

    <h3 class="text-lg font-bold mb-2 text-[var(--foreground)]">🧪 Lab Instructions</h3>
    <div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
        <ul class="list-disc pl-5 text-[var(--muted-foreground)] space-y-1">
            <li>Launch the Simulator and go to <strong>M6: SOME/IP Adaptive</strong>.</li>
            <li>On the Server ECU, click <strong>OfferService()</strong> to broadcast the service.</li>
            <li>On the Client ECU, click <strong>FindService()</strong> to discover it.</li>
            <li>Subscribe to the SpeedChanged event to watch the Ethernet packet flow between the Proxy and Skeleton!</li>
        </ul>
    </div>
  `
};

function startSession(idx) {
  closeModal();
  showTab('session');
  document.getElementById('session-title').textContent = modules[idx].title;
  document.getElementById('session-content').innerHTML = sessionData[idx] || '<p>Content coming soon...</p>';
}
"""

def inject_feature(html_path):
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'id="tab-session"' not in content:
            content = content.replace(
                '<!-- ── QUIZ TAB ── -->',
                session_html + '\n\n  <!-- ── QUIZ TAB ── -->'
            )

        if 'const sessionData =' not in content:
            content = content.replace(
                '/* ─────────────────────────────────────── */\n/*  State',
                session_data_js + '\n\n/* ─────────────────────────────────────── */\n/*  State'
            )

        if 'Take Quiz' in content and 'Start Learning Session' not in content:
            old_buttons = """<button onclick="closeModal();showTab('quiz');startQuiz(${idx})" class="flex-1 border border-[var(--border)] text-xs py-2 rounded hover:bg-[var(--sidebar)]">
        📝 Take Quiz
      </button>"""
            new_buttons = """<button onclick="startSession(${idx})" class="flex-1 border border-[var(--primary)] text-[var(--primary)] text-xs py-2 rounded hover:bg-[var(--sidebar)] transition font-bold">
        📖 Start Learning Session
      </button>
      <button onclick="closeModal();showTab('quiz');startQuiz(${idx})" class="flex-1 border border-[var(--border)] text-xs py-2 rounded hover:bg-[var(--sidebar)]">
        📝 Take Quiz
      </button>"""
            content = content.replace(old_buttons, new_buttons)
            
        if "'session'" not in content and "['modules','quiz','skills','about']" in content:
            content = content.replace("['modules','quiz','skills','about']", "['modules','quiz','skills','about','session']")
            
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Success: {html_path}")
    except Exception as e:
        print(f"Error processing {html_path}: {e}")

repo_dir = r"C:\Users\sriram\.gemini\antigravity\brain\00609f9d-53b1-4421-9b38-a8920e9fa4cc\scratch\Autosar_simulator"
inject_feature(os.path.join(repo_dir, 'autosar_portal.html'))
inject_feature(os.path.join(repo_dir, 'index.html'))
