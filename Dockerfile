# Stage 1: Build
FROM nvcr.io/nvidia/ai-workbench/python-cuda130:1.0.1 AS builder
RUN apt-get update && apt-get install -y git build-essential libssl-dev
WORKDIR /build
RUN git clone --depth 1 https://github.com/hashcat/hashcat.git .
RUN make

# Stage 2: Runtime
FROM nvcr.io/nvidia/ai-workbench/python-cuda130:1.0.1
WORKDIR /hashcat

# System dependencies
RUN apt-get update && apt-get install -y ocl-icd-libopencl1 clinfo && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --no-cache-dir fastapi uvicorn pydantic

# CRITICAL: Map SBSA/ARM64 Blackwell Libraries
RUN for f in /usr/local/cuda/targets/sbsa-linux/lib/libnvrtc*; do \
        ln -sf "$f" /usr/lib/aarch64-linux-gnu/$(basename "$f"); \
        ln -sf "$f" /usr/lib/aarch64-linux-gnu/$(basename "$f").13.0; \
        ln -sf "$f" /usr/lib/aarch64-linux-gnu/$(basename "$f").12; \
    done && ldconfig

# Copy binary AND all necessary supporting files (including hcstat2)
COPY --from=builder /build/hashcat .
COPY --from=builder /build/*.hcstat2 .
COPY --from=builder /build/modules ./modules
COPY --from=builder /build/OpenCL ./OpenCL
COPY --from=builder /build/charsets ./charsets
COPY app.py .

ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]