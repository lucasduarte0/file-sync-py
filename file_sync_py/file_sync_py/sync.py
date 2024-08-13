import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MirrorHandler(FileSystemEventHandler):
    def __init__(self, source_folder, target_folder):
        self.source_folder = source_folder
        self.target_folder = target_folder

    def sync_folders(self):
        for root, dirs, files in os.walk(self.source_folder):
            relative_path = os.path.relpath(root, self.source_folder)
            target_dir = os.path.join(self.target_folder, relative_path)

            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            for file in files:
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, file)

                if not os.path.exists(target_file) or os.path.getmtime(
                    source_file
                ) > os.path.getmtime(target_file):
                    shutil.copy2(source_file, target_file)
                    print(f"Copied: {source_file} to {target_file}")

    def on_modified(self, event):
        self.sync_folders()

    def on_created(self, event):
        self.sync_folders()

    def on_deleted(self, event):
        # Deleting files if needed
        relative_path = os.path.relpath(event.src_path, self.source_folder)
        target_path = os.path.join(self.target_folder, relative_path)

        if os.path.exists(target_path):
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
                print(f"Deleted directory: {target_path}")
            else:
                os.remove(target_path)
                print(f"Deleted file: {target_path}")

    def on_moved(self, event):
        self.on_deleted(event)
        self.on_created(event)


def main(source_folder, target_folder):
    event_handler = MirrorHandler(source_folder, target_folder)
    observer = Observer()
    observer.schedule(event_handler, source_folder, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    source_folder = input("Enter the source folder: ")
    while not os.path.isdir(source_folder):
        print("Invalid source folder. Please enter a valid directory.")
        source_folder = input("Enter the source folder: ")

    target_folder = input("Enter the target folder: ")
    while not os.path.isdir(target_folder):
        print("Invalid target folder. Please enter a valid directory.")
        target_folder = input("Enter the target folder: ")

    main(source_folder, target_folder)
