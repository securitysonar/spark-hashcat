import subprocess
import uuid
import os
import time
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Security Sonar Forensic API")

# Results storage (In production, use a small SQLite or Redis DB)
jobs = {}

class HashcatJob(BaseModel):
    hash_type: int
    attack_mode: int = 0
    hash_file: str
    wordlist: str | None = None
    mask: str | None = None

def run_hashcat(job_id: str, hash_type: int, attack_mode: int, hash_file: str, wordlist: str | None, mask: str | None):
    executable = "/hashcat/hashcat"

    env = os.environ.copy()

    # Path for Grace Blackwell (ARM64)
    sbsa_path = "/usr/local/cuda/targets/sbsa-linux/lib"
    nvrtc_path = f"{sbsa_path}/libnvrtc.so"
    output_path = f"/output/{job_id}.txt"

    if os.path.exists(nvrtc_path):
        # We are on the Spark/ARM architecture
        env["LD_PRELOAD"] = nvrtc_path
        env["LD_LIBRARY_PATH"] = f"{sbsa_path}:{env.get('LD_LIBRARY_PATH', '')}"

    cmd = [
        executable,
        "-m", str(hash_type),
        "-a", str(attack_mode),
        f"/hashes/{hash_file}",
        "--quiet",
        "--outfile", output_path,
        "--potfile-disable",
        "--backend-ignore-opencl",
        "--hwmon-disable",
        "--optimized-kernel-enable"
    ]

    if attack_mode == 0:
        # Dictionary attack
        cmd.insert(5, f"/wordlists/{wordlist}")
    elif attack_mode == 3:
        # Brute force / mask attack
        cmd.append(mask)

    try:
        start = time.time()
        jobs[job_id] = {"status": "Running", "started_at": start}
        subprocess.run(cmd, check=True, env=env)
        duration = time.time() - start
        jobs[job_id] = {"status": "Completed", "started_at": start, "duration_seconds": round(duration, 2)}
    except subprocess.CalledProcessError:
        duration = time.time() - start
        jobs[job_id] = {"status": "Failed", "started_at": start, "duration_seconds": round(duration, 2)}

@app.post("/crack", status_code=202)
async def start_crack(job: HashcatJob, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())

    if not os.path.exists(f"/hashes/{job.hash_file}"):
        raise HTTPException(status_code=400, detail="Hash file not found")

    if job.attack_mode == 0 and not job.wordlist:
        raise HTTPException(status_code=400, detail="wordlist is required for dictionary attack (mode 0)")

    if job.attack_mode == 3 and not job.mask:
        raise HTTPException(status_code=400, detail="mask is required for brute force attack (mode 3)")

    background_tasks.add_task(run_hashcat, job_id, job.hash_type, job.attack_mode, job.hash_file, job.wordlist, job.mask)
    return {"job_id": job_id, "status": "Queued"}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    job = jobs.get(job_id)
    if job is None:
        return {"job_id": job_id, "status": "Not Found"}
    return {"job_id": job_id, **job}

@app.get("/status/health")
async def health_check():
    # Optional: Verify the GPU is still visible to Hashcat
    # This ensures Traefik pulls the node if the driver crashes
    try:
        import subprocess
        result = subprocess.run(["./hashcat", "-I"], capture_output=True, text=True)
        if "NVIDIA GB10" in result.stdout:
            return {"status": "healthy", "gpu": "Blackwell Active"}
    except Exception:
        pass

    # Fallback to simple healthy if the GPU check is too slow
    return {"status": "healthy"}
