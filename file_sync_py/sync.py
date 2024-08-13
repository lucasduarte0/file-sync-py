import os
import time
import shutil
import logging
import logging.handlers
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MirrorHandler(FileSystemEventHandler):
    def __init__(self, source_folder, target_folder):
        self.source_folder = source_folder
        self.target_folder = target_folder
        logging.info("Mirroring started")

    def sync_folders(self):
        try:
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
                        logging.info(f"Copied: {source_file} to {target_file}")
        except Exception as e:
            logging.error(f"Error during folder synchronization: {e}", exc_info=True)

    def on_modified(self, event):
        try:
            self.sync_folders()
        except Exception as e:
            logging.error(f"Error on modified event: {e}", exc_info=True)

    def on_created(self, event):
        try:
            self.sync_folders()
        except Exception as e:
            logging.error(f"Error on created event: {e}", exc_info=True)

    def on_deleted(self, event):
        try:
            relative_path = os.path.relpath(event.src_path, self.source_folder)
            target_path = os.path.join(self.target_folder, relative_path)

            if os.path.exists(target_path):
                if os.path.isdir(target_path):
                    shutil.rmtree(target_path)
                    logging.info(f"Deleted directory: {target_path}")
                else:
                    os.remove(target_path)
                    logging.info(f"Deleted file: {target_path}")
        except Exception as e:
            logging.error(f"Error on deleted event: {e}", exc_info=True)

    def on_moved(self, event):
        try:
            self.on_deleted(event)
            self.on_created(event)
        except Exception as e:
            logging.error(f"Error on moved event: {e}", exc_info=True)


def start_sync(source_folder, target_folder):
    try:
        event_handler = MirrorHandler(source_folder, target_folder)
        observer = Observer()
        observer.schedule(event_handler, source_folder, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        except Exception as e:
            logging.error(f"Error during syncing loop: {e}", exc_info=True)
        finally:
            observer.join()

    except Exception as e:
        logging.critical(f"Critical error in start_sync: {e}", exc_info=True)
