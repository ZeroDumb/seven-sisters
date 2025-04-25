import os
import datetime

BASE_OUTPUT_DIR = os.path.join(os.getcwd(), "output")


def init_output_dir(target):
    """Creates a unique output folder per target."""
    target_dir = os.path.join(BASE_OUTPUT_DIR, target)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir


def write_output(sister_name, target, content):
    """Writes formatted output to the sister's target-specific log file."""
    target_dir = init_output_dir(target)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = os.path.join(target_dir, f"{sister_name}.log")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {sister_name}: {content}\n")


if __name__ == "__main__":
    # Quick test
    target = "example.com"
    sister = "Harley"
    content = "Test boom complete. Zero survivors."
    write_output(sister, target, content)
    print(f"Output written for {sister} at {target}")
