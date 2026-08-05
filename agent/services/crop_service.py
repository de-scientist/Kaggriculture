def plant(tile: dict, crop: str) -> dict:
    return {"kind": "PLANT", "crop": crop}


def water(tile: dict) -> dict:
    return {"kind": "WATER"}


def harvest(tile: dict) -> dict:
    return {"kind": "HARVEST"}


def fertilize(tile: dict) -> dict:
    return {"kind": "FERTILIZE"}


def dig(tile: dict) -> dict:
    return {"kind": "DIG"}
