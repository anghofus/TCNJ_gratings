import screeninfo

def print_monitor_info():
    monitors = screeninfo.get_monitors()
    for i, monitor in enumerate(monitors):
        print(f"Monitor {i}:")
        print(f"  Width: {monitor.width}")
        print(f"  Height: {monitor.height}")
        print(f"  x: {monitor.x}")
        print(f"  y: {monitor.y}")

print_monitor_info()