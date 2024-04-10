from poc import get_posts


def test_get_posts_smoke():
    response = get_posts(limit=2)

    assert len(response) == 2
    assert response[0].ticker == 'WSE:LPP'
    assert response[1].ticker == 'NASDAQ:EQIX'
    assert response[0].link == 'https://hindenburgresearch.com/lpp/'
    assert response[1].link == 'https://hindenburgresearch.com/equinix/'
