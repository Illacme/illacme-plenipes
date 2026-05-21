import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from core.runtime.engine_factory import EngineFactory
engine = EngineFactory.create_engine("imprints/luminous_domain/configs/config.imprint.yaml", imprint_id="luminous_domain")

import core.api.routes.content as content
content.get_global_engine = lambda: engine

full = content.get_galaxy_graph(mode="full")
for n in full.get("nodes", []):
    print("ID:", n["id"], "Title:", n.get("title"))

