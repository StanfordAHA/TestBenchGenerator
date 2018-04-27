import shutil
import pytest
import util
import delegator

def pytest_addoption(parser):
    parser.addoption("--rtl-directory", help="Path to top.v")
    parser.addoption('--files-to-copy', nargs='+', help='Files to copy to rtl-directory')
    parser.addoption('--with-trace', action="store_true")
    parser.addoption('--force-verilate', action="store_true")
    parser.addoption('--clean', action="store_true")

@pytest.fixture
def with_trace(request):
    return request.config.getoption("--with-trace")

@pytest.fixture
def clean(request):
    return request.config.getoption("--clean")

@pytest.fixture
def force_verilate(request):
    return request.config.getoption("--force-verilate")

@pytest.fixture
def rtl_directory(request):
    return request.config.getoption("--rtl-directory")

@pytest.fixture
def files_to_copy(request):
    return request.config.getoption("--files-to-copy")

@pytest.fixture(scope="session", autouse=True)
def setup(request):
    if clean:
        delegator.run(f"rm -rf build/*")
    shutil.copy("../jtag/jtagdriver.h", "build/")
    rtl_directory = request.config.getoption("--rtl-directory")
    files_to_copy = request.config.getoption("--files-to-copy")

    for file in files_to_copy:
        shutil.copy(file,  f"{rtl_directory}/")
