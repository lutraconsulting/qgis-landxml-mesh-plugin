from pathlib import Path

import pytest


@pytest.fixture
def test_data_folder() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture
def test_data_clean(test_data_folder: Path) -> str:
    file_path = test_data_folder / "Example_Clean.xml"
    return file_path.as_posix()


@pytest.fixture
def test_data_mesh2dm(test_data_folder: Path) -> str:
    file_path = test_data_folder / "mesh.2dm"
    return file_path.as_posix()
