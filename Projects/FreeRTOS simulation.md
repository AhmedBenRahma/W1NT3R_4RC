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
Main.C


## 💻 Code (`main/main.c`)

<details>
<summary>Click to expand main.c</summary>

```c
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "main.h"

static uint32_t iters_per_ms;

static void spin_iteration(uint32_t n)
{
    for (uint32_t i = 0; i < n; i++)
        __asm__ __volatile__("NOP");
}

static void calibrate(void)
{
    const uint32_t N = 20000000;
    int64_t t0 = esp_timer_get_time();
    spin_iteration(N);
    int64_t us = esp_timer_get_time() - t0;
    iters_per_ms = (uint32_t)((int64_t)N * 1000 / us);
}

void busyWork(uint32_t worker_ms)
{
    spin_iteration(iters_per_ms * worker_ms);   /* fixed CPU work */
}

static const task_params_t taskA = {.name = "A", .period = 500, .worker = 190};
static const task_params_t taskB = {.name = "B", .period = 300, .worker = 90};

void periodic_task(void *pvParameters)
{
    const task_params_t *p = (const task_params_t *)pvParameters;
    const TickType_t period_ticks = pdMS_TO_TICKS(p->period);
    TickType_t last_wake = xTaskGetTickCount();

    for (uint32_t job = 0;; job++)
    {
        TickType_t start_tick = xTaskGetTickCount();
        int64_t t0 = esp_timer_get_time();
        busyWork(p->worker);
        int64_t dt_us = esp_timer_get_time() - t0;      /* measured before printf */
        TickType_t end_tick = xTaskGetTickCount();

        printf("%s job %lu: start=%lu end=%lu measured=%lld us\n",
               p->name, (unsigned long)job,
               (unsigned long)start_tick, (unsigned long)end_tick, (long long)dt_us);

        vTaskDelayUntil(&last_wake, period_ticks);
    }
}

void app_main(void)
{
    calibrate();
    printf("tick rate=%d Hz, tick=%d ms\n", (int)configTICK_RATE_HZ, (int)(1000 / configTICK_RATE_HZ));
    printf("ticks: 500ms=%lu 300ms=%lu 190ms=%lu 90ms=%lu\n",
           (unsigned long)pdMS_TO_TICKS(500), (unsigned long)pdMS_TO_TICKS(300),
           (unsigned long)pdMS_TO_TICKS(190), (unsigned long)pdMS_TO_TICKS(90));

    xTaskCreatePinnedToCore(periodic_task, "Task A", 4096, (void *)&taskA, TASK_PRIO_2, NULL, 0);
    xTaskCreatePinnedToCore(periodic_task, "Task B", 4096, (void *)&taskB, TASK_PRIO_3, NULL, 0);
}
```

</details>

`main.h` defines `task_params_t` (name, period, worker) and the priority macros `TASK_PRIO_2` and `TASK_PRIO_3`.

## 🧠 Takeaways
- RM is achievable in theory and observed here, but the implementation only **approximates** it: tick quantization (10 ms), context switch and `printf` overhead, and QEMU timing is not hardware timing.
- RM analysis assumes **one processor**: on a dual-core target the tasks must be pinned to one core.
- Equal priorities mean round-robin time slicing in FreeRTOS, which is not RM.
- The critical instant (A and B released together) was never reached because of the phase offset from task creation order.

## ⏭️ Next
- Run it on the real ESP32-S2 board and compare with QEMU
- Lab 3
