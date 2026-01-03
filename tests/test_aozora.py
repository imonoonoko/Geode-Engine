
from src.body.aozora_harvester import AozoraHarvester

def test_aozora_init():
    """初期化テスト"""
    harvester = AozoraHarvester()
    assert len(harvester.WORKS) > 30, "作品リストが少なすぎます"
    assert harvester.cooldown == 300.0

def test_aozora_get_random_work():
    """作品選択テスト"""
    harvester = AozoraHarvester()
    work = harvester._get_random_work()
    assert work is not None
    assert len(work) == 3
    # AuthorID, WorkID, Title
    assert isinstance(work[0], int)
    assert isinstance(work[1], int)
    assert isinstance(work[2], str)

def test_aozora_resolve_url():
    """URL解決テスト (ネットワークアクセスなしで形式だけ確認したいが、実アクセスも許容)"""
    harvester = AozoraHarvester()
    # 走れメロス (35, 1567)
    url = harvester._resolve_file_url(35, 1567)
    assert url is not None
    assert "aozora.gr.jp" in url
    assert "html" in url
