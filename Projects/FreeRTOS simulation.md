FreeRTOS periodic tasks and Rate Monotonic scheduling

📅 2026-10-29 | 🏷️ RTOS, FreeRTOS, ESP-IDF, QEMU, scheduling | 

## 🎯 Goal
Run two periodic tasks on FreeRTOS (ESP-IDF) and check whether theoretical
Rate Monotonic (RM) scheduling is achievable on a real implementation.

| Task | Period | CPU time |
|------|--------|----------|
| A    | 500 ms | 190 ms   |
| B    | 300 ms | 90 ms    |

## 🧰 Setup
- ESP-IDF v5.5.1 on WSL2 (Ubuntu), `idf.py` for build, simulation and monitor
- QEMU (Espressif fork), target `esp32`, because QEMU doesn't emulate the ESP32-S2
- Tick rate: 100 Hz (1 tick = 10 ms)

[Tick rate and conversions]<img width="1165" height="266" alt="image" src="https://github.com/user-attachments/assets/9e5d1191-3e0f-4303-a066-bb774d44c7e7" />

## 🛠️ Approach
1. **One task function, two `xTaskCreate` calls**: the period and workload are passed as parameters.
2. **`vTaskDelayUntil()`** gives drift-free periodic releases (`vTaskDelay()` would add the execution time to the period).
3. **RM priorities**: shorter period means higher priority, so B = 3 and A = 2.
4. **`busyWork()`**: a NOP loop calibrated once with `esp_timer_get_time()`, so it burns CPU work and not wall-clock time. `printf()` stays outside the measured part.
5. **Tasks pinned to core 0** to imitate the single-core ESP32-S2.

![app_main with pinned tasks]<img width="910" height="236" alt="image" src="https://github.com/user-attachments/assets/63a69e83-0c5e-46b8-bcc1-e658aa61de38" />


## 📐 Theory
- U = 190/500 + 90/300 = **0.68** < 0.828 (Liu & Layland bound for n = 2), so it is schedulable
- Response time of A = 190 + 90 = **280 ms** ≤ 500 ms
- Response time of B = 90 ms ≤ 300 ms

## 📊 Results (QEMU)
| Measure | Requested | Observed |
|---------|-----------|----------|
| B, not preempted | 90 ms | ~85–88 ms |
| A, not preempted | 190 ms | ~183–189 ms |
| A, preempted by B | 280 ms (theory) | **275–281 ms** |
| Missed deadlines | 0 | 0 |

Releases are exactly periodic: A every 50 ticks and B every 30 ticks, no drift.

![Final log, A preempted by B]<img width="920" height="150" alt="image" src="https://github.com/user-attachments/assets/7158acbc-d893-43cc-8502-0e3aa0a7d3b8" />




## 🧠 Takeaways
- RM is achievable in theory and observed here, but the implementation only **approximates** it: tick quantization (10 ms), context switch and `printf` overhead, and QEMU timing is not hardware timing.
- RM analysis assumes **one processor**: on a dual-core target the tasks must be pinned to one core.
- Equal priorities mean round-robin time slicing in FreeRTOS, which is not RM.
- The critical instant (A and B released together) was never reached because of the phase offset from task creation order.

## ⏭️ Next
- Run it on the real ESP32-S2 board and compare with QEMU
- Lab 3
