# gRPC Prime Numbers: Python Server and Java Client

A small distributed-systems project built for the **Systèmes et Applications Répartis** course at ENSI. A **Python** gRPC server computes prime-number results, and a **Java** client (written by a classmate) calls it from another computer on the same network.

> Tested across two machines: the server ran on one laptop (Windows, PowerShell) and the client on a different laptop, both on the same Wi-Fi network.

---

## Table of contents

1. [Architecture](#architecture)
2. [The services](#the-services)
3. [Project structure](#project-structure)
4. [Requirements](#requirements)
5. [Server setup (Python)](#server-setup-python)
6. [Network setup](#network-setup)
7. [Client setup (Java)](#client-setup-java)
8. [Usage and expected output](#usage-and-expected-output)
9. [Troubleshooting](#troubleshooting)
10. [What I learned](#what-i-learned)
11. [Author](#author)

---

## Architecture

```
┌────────────────────┐      gRPC over HTTP/2       ┌────────────────────┐
│  Java client       │  ───────────────────────▶   │  Python server     │
│  (friend's laptop) │      TCP port 50051         │  (my laptop)       │
│  menu + stubs      │  ◀───────────────────────   │  prime logic       │
└────────────────────┘      Protobuf messages      └────────────────────┘
```

Both sides share one contract, [`proto/prime.proto`](proto/prime.proto). Code is generated from it in each language (`prime_pb2*.py` for Python, `*Grpc.java` for Java), so the two programs agree on every message and method.

The server never needs the client's IP address. The client needs the **server's** IP address and port.

## The services

| Service | RPC | Type | Input | Output |
|---|---|---|---|---|
| `IsPrimeService` | `IsPrime` | Unary | `GetNumber { int64 n }` | `output { bool b; repeated int64 fact }`: whether `n` is prime, and its prime factors if not |
| `FirstPrimeService` | `FirstPrime` | Unary | `GetNumber { int64 n }` | `NPremiers { repeated int64 range }`: the first `n` primes in one response |
| `FirstPrimeStreamService` | `FirstPrimeStream` | Server streaming | `GetNumber { int64 n }` | stream of `NPremiersStream { int64 range }`: the first `n` primes, one message per prime |

Example: `IsPrime(91)` returns `b = false`, `fact = [7, 13]`.

## Project structure

```
tp-grpc-primes/
├── README.md
├── proto/
│   └── prime.proto            # the shared contract
├── server/
│   ├── server.py              # Python gRPC server (port 50051)
│   └── requirements.txt       # grpcio, grpcio-tools
├── client-java/
│   └── PrimeClient.java       # Java menu client
└── .gitignore
```

The generated files `prime_pb2.py` and `prime_pb2_grpc.py` are not stored in the repository. You create them with the command in the next section.

## Requirements

- Python 3.9+ with `pip`
- Python packages: `grpcio`, `grpcio-tools`
- Java 11+ and Maven or Gradle (for the client, with the `grpc-netty-shaded`, `grpc-protobuf` and `grpc-stub` dependencies and the protobuf plugin)
- Two computers on the same network (or one computer, using `localhost`)

## Server setup (Python)

From the `server/` folder:

```powershell
pip install -r requirements.txt
```

Generate the Python gRPC code from the proto file:

```powershell
python -m grpc_tools.protoc -I ../proto --python_out=. --grpc_python_out=. ../proto/prime.proto
```

This creates `prime_pb2.py` and `prime_pb2_grpc.py` next to `server.py`.

Start the server:

```powershell
python server.py
```

Expected output:

```
gRPC server listening on port 50051
```


The server listens on `[::]:50051`, which means every network address of the machine, so it accepts connections from other computers. Nothing in `server.py` has to be changed to add the client's IP.

## Network setup

**1. Find the server's IP address** (on the server machine):

```powershell
ipconfig
```

Use the **IPv4 Address** of the active Wi-Fi or Ethernet adapter, for example `192.168.1.23`.


**2. Allow the port through Windows Firewall** (PowerShell opened as **Administrator**):

```powershell
New-NetFirewallRule -DisplayName "gRPC 50051" -Direction Inbound -Protocol TCP -LocalPort 50051 -Action Allow
```


Also make sure the Wi-Fi network is set to **Private**. Windows blocks incoming connections on Public networks.

**3. Test the connection from the client machine:**

```powershell
Test-NetConnection -ComputerName SERVER_IP -Port 50051
```

You must see `TcpTestSucceeded : True` before testing the Java client.


## Client setup (Java)

1. Copy `proto/prime.proto` into the Java project (`src/main/proto/`).
2. In the Java copy only, add these two lines under `syntax = "proto3";` so the generated classes land in the right package. They change class names, not the wire protocol:
   ```proto
   option java_multiple_files = true;
   option java_package = "tp_grpc.prime_client";
   ```
3. Build the project so the classes (`IsPrimeServiceGrpc`, `GetNumber`, ...) are generated.
4. In `PrimeClient.java`, set the server's IP:
   ```java
   ManagedChannel channel = ManagedChannelBuilder
           .forAddress("SERVER_IP", 50051)
           .usePlaintext()      // the server uses an insecure port
           .build();
   ```
5. Run `PrimeClient` from the IDE, or with `mvn compile exec:java` / `gradle run`.

## Usage and expected output

Start the server first, then the client. The client shows a menu:

```
===== PRIME NUMBER CLIENT =====
1. Check if a number is prime
2. Get the first n primes (unary)
3. Get the first n primes (streaming)
0. Exit
Choose an option:
```


| Input | Result |
|---|---|
| `1`, then `91` | `91 is not prime.` / `Prime factors: [7, 13]` |
| `1`, then `7` | `7 is prime.` |
| `1`, then `1` | `1 is not prime.` / `No prime factorization returned for this input.` |
| `2`, then `10` | `First 10 primes:` / `[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]` |
| `3`, then `5` | `Streaming primes:` then `2`, `3`, `5`, `7`, `11` on separate lines |
| `0` | The client exits |

The results are printed on the **client's** terminal. The server terminal stays quiet unless you add `print(...)` lines in the service methods.

**Server-side logs (optional)**

Adding `print("IsPrime called with", request.n)` at the start of each method makes the server show each request, for example `IsPrime called with 91`.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `UNAVAILABLE`, connection refused, or timeout | Firewall, wrong IP, server not running, or Wi-Fi client isolation | Check the IP, create the firewall rule, run `Test-NetConnection` |
| `UNAVAILABLE` with an SSL or handshake error | Missing `usePlaintext()` in the client | Add `.usePlaintext()` |
| `UNIMPLEMENTED` | The two `.proto` files differ | Use the same `prime.proto` on both sides |
| `Access denied` when creating the firewall rule | PowerShell is not elevated | Run PowerShell as Administrator |
| `ModuleNotFoundError: prime_pb2` | Python code not generated | Run the `grpc_tools.protoc` command |
| `InputMismatchException` in the client | Letters typed where a number is expected | Type a number (a known limitation of the simple client) |

## What I learned

- How a `.proto` file acts as a language-neutral contract between a Python server and a Java client.
- The difference between **unary** and **server-streaming** RPCs, and when streaming is useful.
- How to run a gRPC service across two machines: server IP, port binding, firewall rules and network profiles.
- How to diagnose connection problems with gRPC status codes and `Test-NetConnection`.

## Author

**Ahmed Ben Rahma**, ENSI (École Nationale des Sciences de l'Informatique), Tunis.
Course: Systèmes et Applications Répartis.
Java client by a classmate.
