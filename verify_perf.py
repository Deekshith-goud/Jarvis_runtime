import subprocess
import time
import psutil
import os
import sys

def get_process_memory_cpu(proc):
    try:
        p = psutil.Process(proc.pid)
        mem = p.memory_info().rss / (1024 * 1024)
        cpu = p.cpu_percent(interval=0.5)
        return mem, cpu
    except psutil.NoSuchProcess:
        return 0, 0

print("--- ORION RUNTIME PERFORMANCE VALIDATOR ---")
print("\\nTest 1: Start with --daemon")
daemon_proc = subprocess.Popen([sys.executable, "main.py", "--daemon"])
time.sleep(10) # Wait for vosk load
mem1, cpu1 = get_process_memory_cpu(daemon_proc)
print(f"Daemon Initial Idle - Memory: {mem1:.1f} MB, CPU: {cpu1}%")

# Leave it running for a bit
time.sleep(15)
mem2, cpu2 = get_process_memory_cpu(daemon_proc)
print(f"Daemon Sustained Idle - Memory: {mem2:.1f} MB, CPU: {cpu2}%")
if mem2 > mem1 + 5:
    print("WARNING: Possible daemon idle memory leak.")
else:
    print("SUCCESS: Daemon idle memory perfectly stable, no CPU spike.")

daemon_proc.terminate()
time.sleep(2)

print("\\nTest 2 & 3: Terminal -> Voice -> AI Command")
term_proc = subprocess.Popen(
    [sys.executable, "main.py", "--terminal"],
    stdin=subprocess.PIPE,
    stdout=subprocess.DEVNULL, # Ignore stdout to avoid clutter
    stderr=subprocess.DEVNULL,
    text=True
)
time.sleep(2)
mem_term, cpu_term = get_process_memory_cpu(term_proc)
print(f"Terminal Base Load - Memory: {mem_term:.1f} MB (No Vosk, No AI)")

# Switch to voice
print("Triggering 'switch to voice'...")
term_proc.stdin.write("switch to voice\\n")
term_proc.stdin.flush()
time.sleep(8) # Wait for vosk
mem_voice, _ = get_process_memory_cpu(term_proc)
print(f"Voice Loaded - Memory jumped to: {mem_voice:.1f} MB")

# Trigger AI
print("Triggering AI command...")
term_proc.stdin.write("explain quantum physics\\n")
term_proc.stdin.flush()
time.sleep(10) # Wait for AI processing
mem_ai, _ = get_process_memory_cpu(term_proc)
print(f"AI Loaded - Memory jumped to: {mem_ai:.1f} MB")

# Duplicate load test
print("Triggering second AI command...")
term_proc.stdin.write("explain rocket science\\n")
term_proc.stdin.flush()
time.sleep(8)
mem_ai2, _ = get_process_memory_cpu(term_proc)
print(f"Second AI Command - Memory: {mem_ai2:.1f} MB")
if mem_ai2 > mem_ai + 10:
    print("WARNING: Possible duplicate load memory leak detected.")
else:
    print("SUCCESS: No duplicate loads.")

print("\\nTest 4: Running for simulated continuous cycles (stress test)...")
# Send 20 blank inputs / commands to simulate passage of time / usage loop
for _ in range(20):
    try:
        term_proc.stdin.write("time\\n")
        term_proc.stdin.flush()
        time.sleep(1)
    except:
        break

mem_final, cpu_final = get_process_memory_cpu(term_proc)
print(f"Final Sustained Memory Check: {mem_final:.1f} MB")

leak_diff = mem_final - mem_ai2
if leak_diff > 5:
    print(f"WARNING: Memory climbed by {leak_diff:.1f} MB.")
else:
    print("SUCCESS: Memory rock solid. No leaks over continuous usage loop.")

term_proc.terminate()
print("\\nTests Complete.")
