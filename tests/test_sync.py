import os
import shutil
import pytest
from unittest.mock import MagicMock, patch
from file_sync_py.sync import MirrorHandler


@pytest.fixture
def setup_test_dirs(tmpdir):
    # Setup source and target directories
    source_folder = tmpdir.mkdir("source")
    target_folder = tmpdir.mkdir("target")

    # Create a test file in the source directory
    test_file = source_folder.join("test_file.txt")
    test_file.write("This is a test file.")

    return str(source_folder), str(target_folder)


def test_sync_folders(setup_test_dirs):
    source_folder, target_folder = setup_test_dirs

    handler = MirrorHandler(source_folder, target_folder)
    handler.sync_folders()

    # Check that the file was copied to the target folder
    copied_file_path = os.path.join(target_folder, "test_file.txt")
    assert os.path.exists(copied_file_path)
    with open(copied_file_path, "r") as file:
        content = file.read()
    assert content == "This is a test file."


def test_on_modified(setup_test_dirs):
    source_folder, target_folder = setup_test_dirs

    handler = MirrorHandler(source_folder, target_folder)

    # Mock the sync_folders method to verify it is called
    handler.sync_folders = MagicMock()
    handler.on_modified(None)

    handler.sync_folders.assert_called_once()


def test_on_created(setup_test_dirs):
    source_folder, target_folder = setup_test_dirs

    handler = MirrorHandler(source_folder, target_folder)

    # Mock the sync_folders method to verify it is called
    handler.sync_folders = MagicMock()
    handler.on_created(None)

    handler.sync_folders.assert_called_once()


def test_on_deleted(setup_test_dirs):
    source_folder, target_folder = setup_test_dirs

    # Manually copy a file to the target folder to simulate a deletion
    target_file_path = os.path.join(target_folder, "test_file.txt")
    shutil.copy2(os.path.join(source_folder, "test_file.txt"), target_file_path)

    handler = MirrorHandler(source_folder, target_folder)

    # Mock the event and os.path.exists
    mock_event = MagicMock()
    mock_event.src_path = os.path.join(source_folder, "test_file.txt")

    handler.on_deleted(mock_event)

    # Check that the file was deleted in the target folder
    assert not os.path.exists(target_file_path)


def test_on_moved(setup_test_dirs):
    source_folder, target_folder = setup_test_dirs

    handler = MirrorHandler(source_folder, target_folder)

    # Mock the sync_folders method and the event
    handler.sync_folders = MagicMock()
    mock_event = MagicMock()
    mock_event.src_path = os.path.join(source_folder, "test_file.txt")

    handler.on_moved(mock_event)

    # Check that the sync_folders method was called
    handler.sync_folders.assert_called()
