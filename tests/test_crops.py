from agent.domain import crop as crop_domain


def test_crop_defaults():
    c = crop_domain.Crop(crop_type="WHEAT")
    assert c.crop_type == "WHEAT"
    assert c.is_mature(current_day=0) is False