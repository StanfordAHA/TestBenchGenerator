import shutil
import pytest
import util

def pytest_addoption(parser):
    parser.addoption("--rtl-directory", help="Path to top.v")
    parser.addoption('--files-to-copy', nargs='+', help='Files to copy to rtl-directory')
    parser.addoption('--trace', action="store_true")
    parser.addoption('--force-verilate', action="store_true")

@pytest.fixture
def trace(request):
    return request.config.getoption("--trace")

@pytest.fixture
def force_verilate(request):
    return request.config.getoption("--force-verilate")

@pytest.fixture
def rtl_directory(request):
    return request.config.getoption("--rtl-directory")

@pytest.fixture
def files_to_copy(request):
    return request.config.getoption("--files-to-copy")

@pytest.fixture(autouse=True)
def setup(rtl_directory, files_to_copy):
    shutil.copy("../jtag/jtagdriver.h", "build/")

    for file in files_to_copy:
        shutil.copy(file,  f"{rtl_directory}/")
