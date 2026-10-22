# Créditos: Arduino y sistemas embebidos

Paquete completo *embedded-engineering-skills*: 43 skills más las carpetas `docs/`, `references/`, `scripts/` y `tests/` del repo original, que las skills consultan con rutas relativas.

Skills escritas por otras personas y copiadas **sin modificaciones** desde sus repos, con permiso de sus licencias. Las licencias completas están en `licencias/`.

| Autor y repo | Licencia | Commit copiado |
|---|---|---|
| Samuel F., [wedsamuel1230/arduino-skills](https://github.com/wedsamuel1230/arduino-skills) | MIT | `869710ec3b9a40a4f14615b68ca1f1d3dfc88323` |

## Skills (43)

| Skill | Para qué sirve (descripción original) |
|---|---|
| `arduino-cli-skill` | Use when users need Arduino CLI commands for board discovery, library installation, compilation, upload, or serial-port troubleshooting on Windows, macOS, or Linux.… |
| `arduino-code-generator` | Generate Arduino and embedded C++ snippets for sensors, actuators, buses, state machines, timing, data logging, and hardware abstraction. Use when a user requests… |
| `arduino-project-builder` | Build complete Arduino and embedded projects across Arduino IDE, Arduino CLI, PlatformIO, and vendor-specific toolchains. Use when users request an application… |
| `arduino-serial-monitor` | Read and analyze Arduino or embedded serial output for structured runtime debugging across Arduino IDE, Arduino CLI, PlatformIO, and vendor-specific monitor tools.… |
| `arduino-workflow-router` | Route Arduino and embedded-system requests across Arduino IDE, Arduino CLI, PlatformIO, and vendor-specific tools. Use when a request combines firmware, board… |
| `battery-selector` | Helps choose the right battery type and charging solution for Arduino/ESP32/RP2040 projects. Use when user asks about battery options, charging circuits, power source… |
| `board-selection` | Use when choosing or replacing an Arduino Uno, Uno R4, ESP32, ESP32-S3, Raspberry Pi Pico, Pico W, or another embedded board from project requirements. Compare exact… |
| `board-support` | Resolve a named Arduino, ESP32, RP2040, or other embedded board to a source-backed exact profile, including pin/peripheral capability, voltage/current, buses,… |
| `bom-generator` | Generates Bill of Materials (BOM) from project descriptions for Arduino/ESP32/RP2040 projects. Use when user needs component lists, parts shopping lists, cost… |
| `boot-flash-recovery` | Diagnose embedded boot, flash layout, image validation and reset loops with a non-destructive recovery path. Use when requests involve bootloader/application offsets,… |
| `bus-debugging` | Diagnose SPI, UART, CAN and I2C protocol failures using transaction evidence and electrical constraints. Use when requests involve corrupt bytes, wrong SPI mode,… |
| `circuit-debugger` | Systematic hardware debugging guide for Arduino/ESP32/RP2040 circuits. Use when user reports: circuit not working, components getting hot, no power, intermittent… |
| `code-review-facilitator` | Automated code review for Arduino/ESP32/RP2040 projects focusing on best practices, memory safety, and common pitfalls. Use when user wants code feedback, says… |
| `datasheet-interpreter` | Extracts key specifications from component datasheet PDFs for maker projects. Use when user shares a datasheet PDF URL, asks about component specs, needs pin… |
| `embedded-build-workflow` | Inspect, reproduce or migrate embedded build workflows with PlatformIO, native ESP-IDF, Arduino CLI, Zephyr/west, Pico SDK, STM32Cube or MicroPython. Use when a… |
| `embedded-project-loop` | Use first when Arduino or embedded hardware work spans sessions, parts delivery, wiring, soldering, flashing, measurements, field tests, recovery, or a durable… |
| `enclosure-designer` | Use when users need a 3D-printable enclosure for an Arduino, ESP32, or RP2040 project and need help with measurements, cutouts, print settings, or environmental… |
| `error-message-explainer` | Explain Arduino and embedded compiler, upload, boot, power, and runtime errors in plain English. Use when a user shares an error or failure from Arduino IDE, Arduino… |
| `fault-forensics` | Analyze embedded panic logs, Cortex-M fault registers, core dumps and addresses against the matching firmware ELF. Use when requests involve HardFault, BusFault,… |
| `field-power-and-connectivity-triager` | Use when maker projects work on USB bench power but fail on their intended supply path, especially for WiFi or sensor-heavy boards such as ESP32, including brownout,… |
| `freertos-patterns` | Use when users need ESP32 FreeRTOS or RP2040 multicore patterns for task creation, queues, synchronization, memory checks, task notifications, or cross-core coordination. |
| `hardware-tdd` | Use when planning tests for Arduino, ESP32, ESP32-S3, Pico, or Pico W firmware; deciding what can run off-target; using Wokwi or simulation; writing host fakes; or… |
| `i2c-bringup-diagnostician` | Use when users need to diagnose I2C bring-up failures on Arduino or ESP32-class boards, including no devices found, wrong readings, address conflicts,… |
| `library-selection` | Use when selecting, replacing, pinning, or auditing an Arduino, ESP32, RP2040, C++, or vendor-framework library. Compare architecture support, framework and version… |
| `memory-budgeting` | Use when Arduino or embedded projects hit SRAM, flash, heap, stack, partition, JSON-buffer, or performance limits, or when reviewing String use, F() placement, OTA… |
| `memory-timing-debugging` | Diagnose runtime heap/stack failures, deadline misses, deadlocks and queue overload in embedded firmware. Use when requests involve leaks, jitter, watchdog… |
| `mermaid-diagram-generator` | Use when users need Mermaid diagrams for Arduino code structure, state machines, timing diagrams, task architecture, or workflow documentation. |
| `micropython-development` | Develop and debug MicroPython firmware and Python applications using mpremote, REPL, board-specific ports and frozen modules. Use when requests involve MicroPython… |
| `non-blocking-patterns` | Use when Arduino or embedded C++ code uses delay(), needs button debouncing, periodic work, cooperative scheduling, watchdog-safe timing, state machines, or… |
| `ota-deployment-guardian` | Use when users need safe over-the-air update workflows for ESP32-class boards or Arduino Uno R4 WiFi, including OTA sketch requirements, network port discovery… |
| `pico-sdk-development` | Build and debug native Raspberry Pi Pico SDK applications with CMake, RP2040/RP2350 targets, PIO and SWD. Use when requests concern Pico SDK configuration, linker… |
| `pin-assignment` | Use when assigning Arduino, ESP32, ESP32-S3, Pico, or Pico W pins; creating a GPIO map; assigning buttons, LEDs, sensors, buses, or actuators; migrating a pin map; or… |
| `power-budget-calculator` | Calculates total power consumption and battery life for Arduino/ESP32/RP2040 projects. Use when user asks about battery life, power requirements, current draw, or… |
| `probe-debugging` | Plan and conduct target-specific GDB, SWD/JTAG and OpenOCD or vendor-probe debugging. Use when requests involve attaching a probe, breakpoints, reset/halt,… |
| `readme-generator` | Auto-generates professional README.md files for Arduino/ESP32/RP2040 projects following open-source best practices. Use when user wants to document their project for… |
| `realtime-control-design` | Design task ownership, control deadlines and overload behavior for an embedded controller running alongside sensors, networking or flash writes. Use when users ask… |
| `sensor-calibration-workbench` | Use when makers need calibration workflows for sensors such as CO2 sensors, load cells, magnetometers, color sensors, or analog sensors, including warm-up behavior,… |
| `sensor-signal-filtering` | Use when the main problem is a noisy or aliased analog/ADC signal and the task needs signal-chain diagnosis or filter-path selection across sampling, anti-aliasing,… |
| `stm32-development` | Build and diagnose STM32Cube HAL/LL projects using their existing CMake, Make, CubeIDE or PlatformIO toolchain. Use when requests involve STM32 clocks, startup/linker… |
| `usb-debugging` | Diagnose embedded USB enumeration, descriptors, CDC/REPL ports and intermittent disconnects. Use when requests involve a missing USB device, wrong interface, native… |
| `wireless-telemetry` | Design and diagnose embedded telemetry, packet freshness and wireless coexistence using UDP, ESP-NOW or a serial bridge. Use when users need AP+STA operation,… |
| `wiring-safety-check` | Use when wiring an Arduino, ESP32, ESP32-S3, Pico, or Pico W to sensors, LEDs, motors, relays, buses, or external supplies, especially when 5 V and 3.3 V logic,… |
| `zephyr-development` | Build and debug Zephyr applications with west, devicetree, Kconfig and versioned workspaces. Use when a request concerns Zephyr board qualifiers, overlays, build… |

## Qué necesitan

- Arduino IDE o `arduino-cli`, o PlatformIO, según el proyecto. Para ESP-IDF, Zephyr, Pico SDK o STM32Cube, sus herramientas oficiales.
- Algunos scripts usan Python 3.10+ (`uv run` o `pip install` de lo que indique cada skill; `datasheet-interpreter` usa httpx y pdfplumber para leer hojas de datos).

## Revisión

Antes de copiarlas revisé licencia, estructura, scripts, llamadas de red, binarios, hooks y frases que intenten darle órdenes ocultas a Claude, sin encontrar problemas. Los scripts no se ejecutaron durante la revisión. Si un autor publica una versión nueva, se puede volver a copiar y actualizar el commit de la tabla. Los enlaces externos son a documentación oficial (Espressif, Arduino, Raspberry Pi, ST) y a tiendas de componentes.
