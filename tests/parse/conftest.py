import tempfile
from pathlib import Path

import pytest
from depender.parse.code import CodeParser


@pytest.yield_fixture(scope="module")
def code_parser():
    code_parser = CodeParser()
    yield code_parser


@pytest.yield_fixture(scope="module")
def package() -> Path:
    with tempfile.TemporaryDirectory() as tmp_dir:
        package_path = Path(tmp_dir) / "package"
        package_path.mkdir()
        yield package_path


@pytest.yield_fixture(scope="module", autouse=True)
def package_content(package: Path):
    """"""
    package.joinpath("__init__.py").touch()
    subpackage1 = package.joinpath("subpackage1")
    subpackage1.mkdir()
    subpackage2 = package.joinpath("subpackage2")
    subpackage2.mkdir()
    module_A = subpackage1.joinpath("A.py")
    module_A.touch()
    with module_A.open("w") as f:
        f.write("from package.subpackage2 import C, D\n")
    module_B = subpackage1.joinpath("B.py")
    module_B.touch()
    module_C = subpackage2.joinpath("C.py")
    module_C.touch()
    with module_C.open("w") as f:
        f.write("from package.subpackage1 import B\n")
    module_D = subpackage2.joinpath("D.py")
    module_D.touch()
    with module_D.open("w") as f:
        f.write("from package.subpackage2 import C\n")
        f.write("from package.subpackage1 import B\n")
