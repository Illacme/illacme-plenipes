
import os

# 模拟 config 中的配置
vault_root = "/Volumes/Notebook/omni-hub/content-vault"
route_matrix = [
    {"source": "Docs", "prefix": "i18n/{lang}/docusaurus-plugin-content-docs/current/{sub_dir}"},
    {"source": "Blog", "prefix": "i18n/{lang}/docusaurus-plugin-content-blog/{sub_dir}"},
    {"source": "Index", "prefix": "i18n/{lang}/docusaurus-plugin-content-pages/{sub_dir}"}
]

# 用户提供的文件路径
test_path = "/Volumes/Notebook/omni-hub/content-vault/Blog/Github/1 小时速成官网的极客工作流.md"

def _find_route_info_for_path(abs_path, vault_root, route_matrix):
    norm_abs = os.path.normcase(os.path.abspath(abs_path))
    sorted_matrix = sorted(route_matrix, key=lambda x: len(x.get('source', '')), reverse=True)
    
    print(f"Norm Abs: {norm_abs}")
    
    for route_cfg in sorted_matrix:
        src = route_cfg.get('source', '')
        route_abs = os.path.normcase(os.path.abspath(os.path.join(vault_root, src)))
        # 这里补上了尾随斜杠逻辑
        route_dir = route_abs if route_abs.endswith(os.sep) else route_abs + os.sep
        
        print(f"Checking against Route Dir: {route_dir}")
        
        if norm_abs.startswith(route_dir):
            return route_cfg.get('prefix', ''), src
    return None, None

prefix, source = _find_route_info_for_path(test_path, vault_root, route_matrix)
print(f"\nResult -> Prefix: {prefix}, Source: {source}")
