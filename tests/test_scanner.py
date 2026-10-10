"""Quick scanner sanity check."""
import os
from sortiq_fs.walker import walk

def test_walk_small_dir(tmp_path):
    (tmp_path / "a.txt").write_text("hello")
    entries, stats = walk(str(tmp_path), recursive=False)
    assert stats.files >= 1
