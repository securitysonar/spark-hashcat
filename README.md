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

Submit an iTunes Backup (Mode 14700) crack request via `curl`:

```
curl -X POST http://localhost/crack \
     -H "Content-Type: application/json" \
     -d '{
           "hash_type": 14700,
           "hash_file": "iphone_backup.txt",
           "wordlist": "rockyou.txt"
         }'
```

```

{"job_id":"<your-job-id>","status":"Queued"}
```
#### 4. Usage: Wait 30 Seconds and Check the Status of the Job
```
curl -H "Host: forensics.spark.local" http://localhost/status/<insert-your-job-id>

```
------

### 📊 Performance Benchmark (GB10)

| **Algorithm**     | **Mode** | **Blackwell Native Speed** | **Notes**                |
| ----------------- | -------- | -------------------------- | ------------------------ |
| **MD5**           | 0        | ~110.5 GH/s                | Raw Compute Throughput   |
| **NTLM**          | 1000     | ~185.2 GH/s                | Enterprise Recovery      |
| **iTunes Backup** | 14700    | ~165.4 kH/s                | High-Iteration PBKDF2    |
| **Argon2id**      | 22500    | 121GB VRAM                 | Unified Memory Advantage |

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

 [SecuritySonar.com](https://securitysonar.com)

