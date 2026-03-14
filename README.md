 ![NVIDIA](https://img.shields.io/badge/NVIDIA-GB10_Grace_Blackwell-76B900?logo=nvidia&logoColor=white)
 ![CUDA Version](https://img.shields.io/badge/CUDA-13.0-green?logo=nvidia&logoColor=white)

## 🚀 Spark-Hashcat: Grace Blackwell Forensic API

------

**A high-performance, containerized Hashcat API engineered specifically for the NVIDIA DGX Spark (or equivalent Dell Pro Max, or Asus Ascent) workstations powered by the Nvidia GB10 Grace Blackwell superchip, designed for AI development.**

------

### ⚖️ Legal Disclaimer

**This software is intended for lawful purposes only.**

Use of this tool is strictly limited to authorized activities, including but not limited to:

- **Digital forensics investigations** conducted by law enforcement or licensed forensic examiners with proper legal authority.
- **Penetration testing and security assessments** performed with explicit written authorization from the system or data owner.
- **Recovery of your own passwords or data** where you have legal ownership or authorization.
- **Academic research and education** in controlled, isolated environments.

**Unauthorized use of this tool to access, crack, or recover credentials belonging to others without explicit permission is illegal** and may violate laws including, but not limited to, the Computer Fraud and Abuse Act (CFAA), the UK Computer Misuse Act, the EU Directive on Attacks Against Information Systems, and equivalent legislation in your jurisdiction.

The author(s) and contributors assume **no liability** for any misuse, damage, or illegal activity arising from the use of this software. By using this software, you agree that you are solely responsible for ensuring your use complies with all applicable local, state, national, and international laws and regulations.

**If you do not agree to these terms, do not use this software.**

------

### 📋 Overview

This project provides a production-ready RESTful API wrapper around Hashcat, optimized to exploit the unique architectural advantages of the DGX Spark. By utilizing the 900 GB/s NVLink-C2C interconnect, this platform eliminates the PCIe bottlenecks common in traditional x86 forensic workstations.

#### 🛡 Strategic Advantages

**Blackwell Native:** Explicitly maps the NVRTC (Real-Time Compiler) to bypass OpenCL fallbacks, unlocking native CUDA performance.

**Unified Memory Mastery:** Leverages the 121GB+ shared memory space for memory-hard algorithms like Argon2id and Scrypt.

**ARM64/SBSA First:** Engineered for the Server Base System Architecture found in NVIDIA Grace CPUs.

**Cloud-Native Orchestration:** Includes Traefik-ready health checks and Docker Compose orchestration for rapid deployment in forensic labs.

------

### 🏗 Project Structure

```
spark-hashcat/
├── data/
│   ├── hashes/          # Volume-mounted forensic evidence
│   └── wordlists/       # High-speed dictionary storage
├── output/              # Successful crack results (JSON/Text)
├── Dockerfile           # Multi-stage ARM64/SBSA build
├── docker-compose.yaml  # GPU-aware service orchestration
├── app.py               # FastAPI asynchronous job handler
└── README.md            # You are here
```

------

### 🚀 Quick Start

#### 1. Prerequisites

- NVIDIA DGX Spark (or compatible Grace Blackwell ARM64 host).
- NVIDIA Container Toolkit installed and configured.
- Access to `nvcr.io` (NVIDIA Container Registry).

#### 2. Deployment

```
# On your DGX Spark clone the Security Sonar repository
git clone https://github.com/securitysonar/spark-hashcat.git
cd spark-hashcat

# Initialize data directories
mkdir -p data/hashes data/wordlists output

# Launch the Blackwell-optimized stack
docker compose up -d --build
```

#### 3. Usage: Submitting a Forensic Job

The `/crack` endpoint accepts the following fields:

| Field         | Type    | Required             | Description                                         |
| ------------- | ------- | -------------------- | --------------------------------------------------- |
| `hash_type`   | integer | Yes                  | Hashcat hash mode (e.g. `1000` for NTLM)            |
| `attack_mode` | integer | No (default: `0`)    | `0` = Dictionary, `3` = Brute Force / Mask          |
| `hash_file`   | string  | Yes                  | Filename in the `/hashes` volume                    |
| `wordlist`    | string  | Required if mode `0` | Filename in the `/wordlists` volume                 |
| `mask`        | string  | Required if mode `3` | Hashcat mask (e.g. `?u?l?l?l?d?d`)                  |

**Dictionary Attack (mode 0)** — Submit an iTunes Backup (Mode 14700) crack request via `curl`:

```
curl -X POST http://localhost/crack \
     -H "Content-Type: application/json" \
     -d '{
           "hash_type": 14700,
           "attack_mode": 0,
           "hash_file": "iphone_backup.txt",
           "wordlist": "rockyou.txt"
         }'
```

**Brute Force / Mask Attack (mode 3)** — Target NTLM hashes with a known pattern (e.g. one uppercase, four lowercase, two digits):

```
curl -X POST http://localhost/crack \
     -H "Content-Type: application/json" \
     -d '{
           "hash_type": 1000,
           "attack_mode": 3,
           "hash_file": "ntlm_hashes.txt",
           "mask": "?u?l?l?l?d?d"
         }'
```

```
{"job_id":"<your-job-id>","status":"Queued"}
```

#### 4. Usage: Check the Status and Duration of the Job

Poll the status endpoint with your job ID. Once complete, the response includes `started_at` (Unix timestamp) and `duration_seconds`:

```
curl http://localhost/status/<insert-your-job-id>
```

**Example response (running):**
```json
{"job_id":"<your-job-id>","status":"Running","started_at":1741910400.5}
```

**Example response (completed):**
```json
{"job_id":"<your-job-id>","status":"Completed","started_at":1741910400.5,"duration_seconds":142.37}
```
------

### 📊 Performance Benchmark (GB10)

| **Algorithm**     | **Mode** | **Blackwell Native Speed** | **Notes**                |
| ----------------- | -------- | -------------------------- | ------------------------ |
| **MD5**           | 0        | 79610.4 MH/s               | Raw Compute Throughput   |
| **NTLM**          | 1000     | 75717.8 MH/s               | < Day for 9 Characters   |
| **IOS 9 backup**  | 14700    | 3342.7 kH/s                | PBKDF2-HMAC-SHA1         |
| **IOS 10> backup**| 14800    | 276 H/s                    | PBKDF2-HMAC-SHA256       |

------

### 🔧 Engineering Deep-Dive: The "NVRTC" Bridge

One of the primary challenges with containerized Blackwell environments is the initialization of the **NVIDIA Real-Time Compiler (NVRTC)**. This project implements a hardware-aware bridge:

1. **SBSA Mapping:** We mount the host's `/usr/local/cuda/targets/sbsa-linux/lib` directly into the container.
2. **Dynamic Loading:** We use `LD_PRELOAD` inside the `app.py` wrapper to ensure the Blackwell-specific JIT compiler is prioritized over generic system libraries.
3. **Unified Memory:** By utilizing the Grace-Blackwell C2C link, we bypass PCIe latency, allowing for near-instantaneous data transfer between the CPU and GPU.

------

### 👤 Author

**Peter Campbell CISSP, CEH** 

*Platform Security Engineer | NVIDIA-Certified Professional (NCP-AIN + NCP-ADS)*
*Security Sonar Research*

[SecuritySonar.com](https://securitysonar.com)

