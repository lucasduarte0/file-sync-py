import os
import daemon
import logging
import logging.handlers
import argparse
from file_sync_py.sync import start_sync


def setup_logging():
    log_file_path = os.path.expanduser("~/file_sync_py/logs/sync.log")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
    # Configure logging to use RotatingFileHandler for logging to a file
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=10**6, backupCount=5
    )
    file_formatter = logging.Formatter('%(asctime)s %(message)s')
    file_handler.setFormatter(file_formatter)

    # Configure logging to output to console (standard output)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s %(message)s')
    console_handler.setFormatter(console_formatter)

    # Get the root logger
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Add both handlers to the root logger
    root.addHandler(file_handler)
    root.addHandler(console_handler)


def main():
    parser = argparse.ArgumentParser(description="File Sync Script")
    parser.add_argument("--daemon", action="store_true", help="Run as a daemon")
    parser.add_argument("--source", help="Source folder")
    parser.add_argument("--target", help="Target folder")
    args = parser.parse_args()

    source_folder = args.source
    if not source_folder:
        source_folder = input("Enter the source folder: ")
        while not os.path.isdir(source_folder):
            print("Invalid source folder. Please enter a valid directory.")
            source_folder = input("Enter the source folder: ")

    target_folder = args.target
    if not target_folder:
        target_folder = input("Enter the target folder: ")
        while not os.path.isdir(target_folder):
            print("Invalid target folder. Please enter a valid directory.")
            target_folder = input("Enter the target folder: ")

    setup_logging()

    if args.daemon:
        with open("/dev/null", "w+") as dev_null:
            with daemon.DaemonContext(
                stdout=dev_null, stderr=dev_null, detach_process=True
            ):
                start_sync(source_folder, target_folder)
    else:
        start_sync(source_folder, target_folder)


if __name__ == "__main__":
    main()
