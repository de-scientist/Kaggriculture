from agent.domain import animal as animal_domain


def build_coop() -> dict:
    return {"kind": "BUILD_COOP"}


def build_pasture() -> dict:
    return {"kind": "BUILD_PASTURE"}


def feed() -> dict:
    return {"kind": "FEED"}


def collect_fertilizer() -> dict:
    return {"kind": "COLLECT_FERTILIZER"}


def care() -> dict:
    return {"kind": "CARE"}