import mdformat
import pytest

HIST_KEY = "mdformat/mtimes"


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption("--mdformat", action="store_true", help="perform markdown format checks on .md files")


def pytest_configure(config):
    if config.option.mdformat:
        config.addinivalue_line("markers", "mdformat: enable format checking with mdformat")
        if hasattr(config, "cache"):
            config._mdformat_mtimes = config.cache.get(HIST_KEY, {})


def pytest_collect_file(path, parent):
    config = parent.config
    if config.option.mdformat and path.ext == ".md":
        if hasattr(MdFormatItem, "from_parent"):
            return MdFormatItem.from_parent(parent, fspath=path)
        else:
            return MdFormatItem(path, parent)


def pytest_unconfigure(config):
    if hasattr(config, "_mdformat_mtimes"):
        config.cache.set(HIST_KEY, config._mdformat_mtimes)


class MdFormatError(Exception):
    """Indicates an error during mdformat checks."""


class MdFormatItem(pytest.Item, pytest.File):
    def __init__(self, fspath, parent):
        super(MdFormatItem, self).__init__(fspath, parent)
        self._nodeid += "::MDFORMAT"
        self.add_marker("mdformat")

    def setup(self):
        pytest.importorskip("mdformat")
        mtimes = getattr(self.config, "_mdformat_mtimes", {})
        self._mdformat_mtime = self.fspath.mtime()
        old = mtimes.get(str(self.fspath), 0)
        if self._mdformat_mtime == old:
            pytest.skip("file(s) previously passed mdformat checks")

    def runtest(self):
        with open(str(self.fspath)) as file:
            md = file.read()
        formatted = mdformat.text(md)
        assert md == formatted
        mtimes = getattr(self.config, "_mdformat_mtimes", {})
        mtimes[str(self.fspath)] = self._mdformat_mtime

    def repr_failure(self, excinfo):
        if excinfo.errisinstance(MdFormatError):
            return excinfo.value.args[0].stdout
        return super(MdFormatItem, self).repr_failure(excinfo)

    def reportinfo(self):
        return self.fspath, -1, "MdFormat check"
