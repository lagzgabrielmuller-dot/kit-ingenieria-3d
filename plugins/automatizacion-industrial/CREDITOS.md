# Créditos: Automatización industrial y robótica

Guías para programar y automatizar PLC y programas de laboratorio, y buenas prácticas de robótica con ROS.

Skills escritas por otras personas y copiadas **sin modificaciones** desde sus repos, con permiso de sus licencias. Las licencias completas están en `licencias/`.

| Autor y repo | Licencia | Commit copiado |
|---|---|---|
| Major AI Skills contributors, [alivirgo/Major-AI-Skills](https://github.com/alivirgo/Major-AI-Skills) | MIT | `17fb963bd185e23367d23b22f2ea5f3688d27f40` |
| arpitg1304, [arpitg1304/robotics-agent-skills](https://github.com/arpitg1304/robotics-agent-skills) | Apache-2.0 | `f9bc5467ff9ee3d23f1a1b0b29a649843bb6ad11` |

## Skills (15)

| Skill | Para qué sirve (descripción original) |
|---|---|
| `codesys` | Develop CODESYS Structured Text and Python ScriptEngine workflows; troubleshoot fieldbus and OPC UA integration in a test environment. |
| `docker-ros2-development` | Best practices for Docker-based ROS2 development including multi-stage Dockerfiles, docker-compose for multi-container robotic systems, DDS discovery across… |
| `labview` | Automate LabVIEW dataflow and build workflows, integrate NI-DAQmx or VISA instruments, and diagnose hardware communication. |
| `opencv` | Build OpenCV image and video processing workflows with transforms, contours, capture, and classical vision operations. |
| `robot-bringup` | Bringing up a complete ROS2 system on a robot's onboard computer: systemd services, launch file composition, ordered startup, and production monitoring. Use this… |
| `robot-perception` | Comprehensive best practices for robot perception systems covering cameras, LiDARs, depth sensors, IMUs, and multi-sensor setups. Use this skill when working with RGB… |
| `robotics-design-patterns` | Architecture patterns, design principles, and proven recipes for building robust robotics software. Use this skill when designing robot software architectures,… |
| `robotics-security` | Security hardening and best practices for robotic systems, covering SROS2 DDS security, network segmentation, secrets management, secure boot, and the physical-cyber… |
| `robotics-software-principles` | Foundational software design principles applied specifically to robotics module development. Use this skill when designing robot software modules, structuring… |
| `robotics-testing` | Testing strategies, patterns, and tools for robotics software. Use this skill when writing unit tests, integration tests, simulation tests, or hardware-in-the-loop… |
| `rockwell-studio-5000` | Work with Studio 5000 Logix projects, L5X files, and pycomm3 communications in an authorized industrial test environment. |
| `ros1` | Best practices, design patterns, and common pitfalls for ROS1 (Robot Operating System 1) development. Use this skill when building ROS1 nodes, packages, launch files,… |
| `ros2` | Comprehensive best practices, design patterns, and common pitfalls for ROS2 (Robot Operating System 2) development. Use this skill when building ROS2 nodes, packages,… |
| `ros2-web-integration` | Patterns and best practices for integrating ROS2 systems with web technologies including REST APIs, WebSocket bridges, and browser-based robot interfaces. Use this… |
| `siemens-tia-portal` | Develop TIA Portal SCL and Openness automation, and inspect SIMATIC communications in an authorized test environment. |

## Qué necesitan

- Los programas de cada skill (TIA Portal, CODESYS, Studio 5000, LabVIEW) instalados con su licencia. Los ejemplos de comunicación usan python-snap7, pycomm3 u OPC UA.
- ROS 2 (o ROS 1) y Docker para las skills de robótica.
- **Seguridad**: probar siempre en un simulador (PLCSIM, CODESYS Control Win) o en un tablero de prueba, nunca escribir variables en una máquina en marcha.

## Revisión

Antes de copiarlas revisé licencia, estructura, scripts, llamadas de red, binarios, hooks y frases que intenten darle órdenes ocultas a Claude, sin encontrar problemas. Los scripts no se ejecutaron durante la revisión. Si un autor publica una versión nueva, se puede volver a copiar y actualizar el commit de la tabla. Busqué en particular instrucciones para atacar o saltear protecciones de PLC y no hay: las skills de Siemens, CODESYS y Rockwell piden trabajar en un entorno de prueba autorizado.
