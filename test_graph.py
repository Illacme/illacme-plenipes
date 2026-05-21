import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from core.config.config import load_config
from core.sources.local_source import LocalSource
from core.editorial.vault_indexer import VaultIndexer

config = load_config('imprints/luminous_domain/configs/config.imprint.yaml', imprint_id='luminous_domain')
source = LocalSource(config.vault_root)
md_index, asset_index, link_graph = VaultIndexer.build_indexes(source, config)

print("Nodes found:", len(link_graph))
for k, v in link_graph.items():
    print(" -", k, v.get("metadata", {}).get("title"))

