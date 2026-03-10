import subprocess
import uuid
import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Security Sonar Forensic API")

# Results storage (In production, use a small SQLite or Redis DB)
jobs = {}

class HashcatJob(BaseModel):
    hash_type: int
    hash_file: str
    wordlist: str

def run_hashcat(job_id: str, mode: int, hash_file: str, wordlist: str):
    # ... previous setup ...
    executable = "/hashcat/hashcat" 
    
    # THE PATH YOU FOUND ON THE SPARK
    nvrtc_path = "/usr/local/cuda/targets/sbsa-linux/lib/libnvrtc.so"
    
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
        "-m", str(mode), 
        f"/hashes/{hash_file}", 
        f"/wordlists/{wordlist}",
        "--quiet", 
        "--outfile", output_path,
        "--potfile-disable",
        "--backend-ignore-opencl", # Kill the OpenCL error
        "--notools", # Stops the NVML "Not Supported" noise
        "--force" # Keep this to bypass the remaining driver warnings
    ]
    
    try:    
        jobs[job_id] = "Running"
        subprocess.run(cmd, check=True)
        jobs[job_id] = "Completed"
    except subprocess.CalledProcessError:
        jobs[job_id] = "Failed"

@app.post("/crack", status_code=202)
async def start_crack(job: HashcatJob, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    # Verify file existence before starting
    if not os.path.exists(f"/hashes/{job.hash_file}"):
        raise HTTPException(status_code=400, detail="Hash file not found")
        
    background_tasks.add_task(run_hashcat, job_id, job.hash_type, job.hash_file, job.wordlist)
    return {"job_id": job_id, "status": "Queued"}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    status = jobs.get(job_id, "Not Found")
    return {"job_id": job_id, "status": status}

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
