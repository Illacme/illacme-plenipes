import sys
import traceback
import signal

def dump_stacks(signal, frame):
    print("\n" + "="*80)
    print("🔥 THREAD DUMP - TRIGGERED BY SIGNAL")
    print("="*80)
    for thread_id, stack in sys._current_frames().items():
        print(f"\nThread ID: {thread_id}")
        for filename, lineno, name, line in traceback.extract_stack(stack):
            print(f'  File: "{filename}", line {lineno}, in {name}')
            if line:
                print(f"    {line.strip()}")
    print("\n" + "="*80)

# 注册信号
signal.signal(signal.SIGUSR1, dump_stacks)
print(f"Registered SIGUSR1 listener in PID {os.getpid()}")
