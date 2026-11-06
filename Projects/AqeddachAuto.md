<div align="center">

# 🍽️ AqeddachAuto

### An autonomous robotic waiter built with Lingua Franca

*CPS 2026 Hackathon · ENSI, Tunisia*

![Platform](https://img.shields.io/badge/platform-Pololu%203pi%2B%202040-blue)
![MCU](https://img.shields.io/badge/MCU-RP2040-green)
![Language](https://img.shields.io/badge/language-Lingua%20Franca%20(C%20target)-orange)
![Status](https://img.shields.io/badge/status-in%20development-yellow)

</div>

---

## Overview

**AqeddachAuto** (*Aqeddac* is the Amazigh word for "waiter", plus *Auto* for autonomous) is a robot that works as a waiter in a small restaurant arena. It takes an order, carries a lightweight cup to the right table, serves it, and returns to the kitchen, without ever dropping the cup.

The arena has **no lines to follow**. The robot navigates with wheel encoders and a gyroscope (dead reckoning), and corrects its position when it detects the square floor marker of a table.

Two robots compete at the same time. The first to serve the correct table **and** return wins. Completion comes first, speed second.

## The mission

| # | Stage | What the robot does |
|---|---|---|
| 1 | **Prepare** | Calibrates the IR and bump sensors, then lets the user pick the robot colour (Blue or Black) |
| 2 | **Take order** | Button A increments the table number, button B confirms. Mission starts 2 s later |
| 3 | **Deliver** | Drives to the requested table, detects its square marker, stops with clearance and faces the table |
| 4 | **Serve** | Plays music, animates the RGB LEDs, waits 3 s, plays a sound, shows "Bon appetit!" |
| 5 | **Return** | Navigates back to the kitchen, avoiding tables, chairs, structures and the other robot, then docks |
| 6 | **Report** | On a button press, prints the whole trajectory over serial, one `timestamp, x, y` per line |

## Hardware
<img width="153" height="204" alt="image" src="https://github.com/user-attachments/assets/54035781-1f6e-49d7-af3f-57887492f712" />
<img width="153" height="204" alt="image" src="https://github.com/user-attachments/assets/d9f7c8d1-958f-4cf9-b715-4bca8215c63e" />


| Component | Role |
|---|---|
| Pololu 3pi+ 2040 robot (RP2040) | Main platform |
| Wheel motors + quadrature encoders | Driving and distance measurement |
| IMU (LSM6DSO: gyroscope + accelerometer) | Heading estimation |
| 5 IR reflectance sensors | Floor marker detection |
| 2 bump sensors | Contact detection (they share emitters with the line sensors, so both cannot be used at once) |
| OLED display, RGB LEDs, buttons A and B | User interface |

## Software architecture

The program is written in **Lingua Franca (LF)**, a coordination language where components (*reactors*) communicate through timed events, and where state machines are written as *modal models*.

```
 Buttons ──> OrderTaker ──> Mission (modal model) ──> Navigator ──> Motors (PI speed control)
                                │                        ▲
 Encoders ─┐                    │                        │
 Gyro ─────┼──> Odometry (x, y, θ) ─────────────────────┘
 IR line ──┴──> MarkerDetector ──> position correction
                                │
                                ├──> Server (sound, LEDs)
                                ├──> PathLogger ──> serial report
                                └──> Display
```

### Main ideas

- **Dead reckoning.** Encoder ticks give the distance travelled by each wheel. The gyroscope gives the heading. Together they give the pose (x, y, θ).
- **Marker correction.** Odometry drifts. When a floor marker is confirmed, the estimated position is reset to that marker's known coordinates.
- **Waypoint routes.** With a handful of tables, routes are stored as a lookup table indexed by start side and table number, instead of running a path-planning algorithm.
- **Smooth motion.** Speeds are ramped up and down, so the cup stays upright.
- **Modal state machine.** Each mission stage is a mode, so only the logic of the active stage runs.

### Differential drive in two lines

```
v     = (v_right + v_left) / 2
omega = (v_right - v_left) / L        (L = distance between the wheels)
```

## Repository structure

```
.
├── src/
│   ├── AqeddachAuto.lf   # main program
│   ├── lib/              # reactors for sensors and actuators
│   └── examples/         # small test programs for each reactor
├── robot-lib/            # C drivers for the Pololu 3pi+ 2040
├── COLLABORATORS.md
└── SOLUTION.md           # technical decisions and test results
```

## Build and flash

Requirements: Lingua Franca `lfc` (0.13.0 used here), CMake, `arm-none-eabi-gcc`, the Raspberry Pi Pico SDK (`PICO_SDK_PATH` set), and `picotool`.

```bash
# generate the C code and compile
lfc src/AqeddachAuto.lf

# flash the robot (hold BOOTSEL while powering it on)
picotool load -x bin/AqeddachAuto.elf
```

The generated folders (`src-gen/`, `bin/`, `include/`) are not committed.

