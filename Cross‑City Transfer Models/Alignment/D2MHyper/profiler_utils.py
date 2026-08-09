import time
import torch

@torch.no_grad()
def measure_inference_and_memory(model, loader, device):
    model.eval()

    # warmup
    warm = 3
    it = iter(loader)
    for _ in range(warm):
        try:
            xt, _ = next(it)
        except StopIteration:
            break
        xt = xt.to(device)
        _ = model(None, xt, only_target=True)

    if torch.cuda.is_available() and "cuda" in str(device):
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.synchronize(device)

    t0 = time.time()
    num_batches = 0
    num_samples = 0

    for xt, _ in loader:
        xt = xt.to(device)
        bs = xt.shape[0]
        _ = model(None, xt, only_target=True)
        num_batches += 1
        num_samples += bs

    if torch.cuda.is_available() and "cuda" in str(device):
        torch.cuda.synchronize(device)
        peak_bytes = torch.cuda.max_memory_allocated(device)
        peak_gb = peak_bytes / (1024 ** 3)
    else:
        peak_gb = 0.0

    total_s = time.time() - t0
    latency_ms_batch = (total_s / max(num_batches, 1)) * 1000.0
    latency_ms_sample = (total_s / max(num_samples, 1)) * 1000.0

    return {
        "peak_gpu_gb": float(peak_gb),
        "infer_total_s": float(total_s),
        "num_batches": int(num_batches),
        "num_samples": int(num_samples),
        "latency_ms_per_batch": float(latency_ms_batch),
        "latency_ms_per_sample": float(latency_ms_sample),
    }
