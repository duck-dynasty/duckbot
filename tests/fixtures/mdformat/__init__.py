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


def pytest_collect_file(file_path, path, parent):
    config = parent.config
    if config.option.mdformat and file_path.suffix == ".md":
        return MdFormatFile.from_parent(parent, path=file_path)


def pytest_unconfigure(config):
    if hasattr(config, "_mdformat_mtimes"):
        config.cache.set(HIST_KEY, config._mdformat_mtimes)


class MdFormatFile(pytest.File):
    def collect(self):
        return [MdFormatItem.from_parent(self, name="mdformat")]


class MdFormatItem(pytest.Item):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
        formatted = mdformat.text(md, extensions={"gfm", "tables"}, codeformatters={"python"})
        assert md == formatted
        mtimes = getattr(self.config, "_mdformat_mtimes", {})
        mtimes[str(self.fspath)] = self._mdformat_mtime
