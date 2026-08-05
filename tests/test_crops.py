from agent.domain import crop as crop_domain


def test_crop_defaults():
    c = crop_domain.Crop()
    assert c.kind == "PLANT"
    assert c.crop == ""