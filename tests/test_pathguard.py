"""Quick PathGuard sanity check — passes on Linux and Windows."""
from sortiq_fs.pathguard import is_blacklisted, normalize

def test_system_dirs_blocked():
    assert is_blacklisted("C:/Windows")
    assert is_blacklisted("C:/Windows/System32")
    assert is_blacklisted("C:/Program Files")
    assert is_blacklisted("C:/Users/All Users/AppData")

def test_normal_path_safe():
    assert not is_blacklisted("D:/Downloads")
    assert not is_blacklisted("D:/AbiLabs/Sortiq")
