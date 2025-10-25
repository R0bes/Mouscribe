from src.utils.logger import get_log_buffer, get_recent_logs, setup_logging

print("Setting up logging...")
setup_logging()

print("Getting log buffer...")
buffer = get_log_buffer()
print("Buffer:", buffer)

print("Getting recent logs...")
logs = get_recent_logs(count=10)
print("Recent logs:", logs)
print("Log count:", len(logs) if logs else 0)

if logs:
    print("First log:", logs[0])
    print("First log message:", logs[0].message)
