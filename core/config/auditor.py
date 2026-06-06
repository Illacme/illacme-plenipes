# -*- coding: utf-8 -*-
"""
Illacme Plenipes Core - Configuration Auditor
职责：提供三层继承关系合并、生效来源分析与密钥安全审计功能。
🛡️ [SOP-01 Compliant]：行数限制在 300 行以下。
"""
import os
import yaml
from core.utils.tracing import SovereignCore, tlog
from core.config.constants import CONFIG_NAME, CONFIG_LOCAL_NAME, CONFIG_IMPRINT_NAME, CONFIG_DIR, IMPRINT_DIR
from core.config.governance_map import resolve_governance_level
from core.governance.credential_wizard import is_sensitive_value, mask_plain_value

def deep_update(d, u):
    """递归更新字典"""
    import collections.abc
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def load_raw_layers(config_path: str, imprint_id: str = None) -> dict:
    """加载三层的原始配置字典 (解密前)"""
    layers = {"global": {}, "local": {}, "imprint": {}}
    
    # 1. Global
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                layers["global"] = yaml.safe_load(f) or {}
        except Exception as e:
            tlog.warning(f"Failed to load global config: {e}")
            
    # 2. Local
    local_paths = [CONFIG_LOCAL_NAME]
    base, _ = os.path.splitext(config_path)
    derived_local = f"{base}.local.yaml"
    if derived_local not in local_paths:
        local_paths.append(derived_local)
        
    local_data = {}
    for lp in local_paths:
        if os.path.exists(lp):
            try:
                with open(lp, 'r', encoding='utf-8') as f:
                    deep_update(local_data, yaml.safe_load(f) or {})
            except Exception as e:
                tlog.warning(f"Failed to load local config: {e}")
    layers["local"] = local_data
    
    # 3. Imprint
    if imprint_id and imprint_id != "default":
        imprint_path = os.path.join(IMPRINT_DIR, imprint_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
        if os.path.exists(imprint_path):
            try:
                with open(imprint_path, 'r', encoding='utf-8') as f:
                    layers["imprint"] = yaml.safe_load(f) or {}
            except Exception as e:
                tlog.warning(f"Failed to load imprint config: {e}")
                
    return layers

def flatten_dict(d: dict, prefix: str = "") -> dict:
    """递归扁平化字典与列表"""
    flat = {}
    if not isinstance(d, dict):
        return flat
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            flat.update(flatten_dict(v, f"{key}."))
        elif isinstance(v, list):
            for idx, item in enumerate(v):
                if isinstance(item, (dict, list)):
                    flat.update(flatten_dict(item, f"{key}.{idx}."))
                else:
                    flat[f"{key}.{idx}"] = item
        else:
            flat[key] = v
    return flat

@SovereignCore
def audit_config_layers(config_manager, imprint_id: str = None) -> dict:
    """执行三层配置的安全继承拓扑分析并返回脱敏审计数据。"""
    config_path = config_manager.config_path if config_manager else CONFIG_NAME
    if not imprint_id and config_manager:
        imprint_id = config_manager.imprint_id
        
    layers = load_raw_layers(config_path, imprint_id)
    
    flat_global = flatten_dict(layers["global"])
    flat_local = flatten_dict(layers["local"])
    flat_imprint = flatten_dict(layers["imprint"])
    
    all_keys = sorted(list(set(flat_global.keys()) | set(flat_local.keys()) | set(flat_imprint.keys())))
    
    items = []
    cleartext_count = 0
    
    for key in all_keys:
        global_val = flat_global.get(key)
        local_val = flat_local.get(key)
        imprint_val = flat_imprint.get(key)
        
        gov_level = resolve_governance_level(key)
        
        # 决策生效来源与生效原始值
        if gov_level == "imprint" and imprint_val is not None:
            source = "imprint"
            raw_val = imprint_val
        elif gov_level == "local" and local_val is not None:
            source = "local"
            raw_val = local_val
        else:
            if local_val is not None:
                source = "local"
                raw_val = local_val
            elif imprint_val is not None:
                source = "imprint"
                raw_val = imprint_val
            elif global_val is not None:
                source = "global"
                raw_val = global_val
            else:
                source = "default"
                raw_val = None
                
        # 敏感性与加密状态识别
        def mask_if_sensitive(k, v):
            if v is None:
                return None
            v_str = str(v).strip()
            if v_str.startswith("enc:") or v_str.startswith("ENC:"):
                return v_str
            last_k = k.split('.')[-1]
            if is_sensitive_value(last_k, v_str):
                return mask_plain_value(v_str)
            return v_str
            
        def check_status(k, v):
            if v is None:
                return "none"
            v_str = str(v).strip()
            if v_str.startswith("enc:") or v_str.startswith("ENC:"):
                return "encrypted"
            last_k = k.split('.')[-1]
            if is_sensitive_value(last_k, v_str):
                return "cleartext"
            return "none"
            
        sec_status = check_status(key, raw_val)
        if sec_status == "cleartext":
            cleartext_count += 1
            
        items.append({
            "key": key,
            "governance_level": gov_level,
            "global_val": mask_if_sensitive(key, global_val),
            "local_val": mask_if_sensitive(key, local_val),
            "imprint_val": mask_if_sensitive(key, imprint_val),
            "merged_val": mask_if_sensitive(key, raw_val),
            "source": source,
            "security_status": sec_status
        })
        
    return {
        "imprint_id": imprint_id or "default",
        "items": items,
        "summary": {
            "total_keys": len(all_keys),
            "cleartext_issues": cleartext_count,
            "has_warnings": cleartext_count > 0
        }
    }

def print_cli_audit_report(audit_data: dict):
    """将配置拓扑与安全审计结果以精美的 Rich 表格格式打印至终端。"""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console()
    
    console.print(f"\n[bold cyan]📊 三层配置安全拓扑审计 ({audit_data['imprint_id']})[/bold cyan]")
    
    if audit_data["summary"]["cleartext_issues"] > 0:
        warning_msg = f"⚠️ [bold red]严重安全警告[/bold red]：在当前配置中检测到 {audit_data['summary']['cleartext_issues']} 处未加密的明文密钥！\n建议立即运行 [bold yellow]python3 plenipes.py --credentials[/bold yellow] 加密以解除主权红线拦截。"
        console.print(Panel(warning_msg, border_style="red", title="[bold red]SECURITY AUDIT CRITICAL[/bold red]"))
        
    table = Table(show_header=True, header_style="bold magenta", box=None)
    table.add_column("配置路径", style="dim", width=40)
    table.add_column("最终生效值", width=25)
    table.add_column("决策来源", width=12)
    table.add_column("安全状态", width=12)
    
    for item in audit_data["items"]:
        src_colors = {"global": "cyan", "local": "green", "imprint": "magenta"}
        src = item["source"]
        src_disp = f"[{src_colors.get(src, 'white')}]{src.upper()}[/{src_colors.get(src, 'white')}]"
        
        sec_status = item["security_status"]
        if sec_status == "encrypted":
            sec_disp = "[green]🔒 已加密[/green]"
        elif sec_status == "cleartext":
            sec_disp = "[bold red]⚠️ 明文密钥[/bold red]"
        else:
            sec_disp = "[dim]普通字段[/dim]"
            
        table.add_row(item["key"], item["merged_val"] or "[dim]None[/dim]", src_disp, sec_disp)
        
    console.print(table)
