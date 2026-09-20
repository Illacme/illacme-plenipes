#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Assembler Resolvers
职责：负责配置字典的深层更新、YAML 包含解析、环境变量展开与秘密字段解密。
"""

import os
import re
import yaml
import collections.abc
from typing import Dict, Any

from core.utils.tracing import tlog
from core.governance.secret_manager import secrets


def deep_update(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
    """
    递归深度更新字典。

    :param d: 待更新的字典
    :param u: 包含更新内容的字典
    :return: 更新后的字典
    """
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def resolve_secrets(data: Any) -> Any:
    """
    递归解析加密的秘密配置字段。

    :param data: 输入的配置数据
    :return: 解析后的数据
    """
    if isinstance(data, str) and data.startswith("enc:"):
        return secrets.decrypt(data)
    elif isinstance(data, dict):
        for k, v in data.items():
            data[k] = resolve_secrets(v)
    elif isinstance(data, list):
        return [resolve_secrets(item) for item in data]
    return data


def resolve_env_vars(data: Any) -> Any:
    """
    递归解析环境变量占位符。

    :param data: 输入的配置数据
    :return: 替换环境变量后的数据
    """
    if isinstance(data, str):
        pattern = re.compile(r'\$\{(.+?)\}')
        def replace(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        return pattern.sub(replace, data)
    elif isinstance(data, dict):
        for k, v in data.items():
            data[k] = resolve_env_vars(v)
    elif isinstance(data, list):
        return [resolve_env_vars(item) for item in data]
    return data


def resolve_includes(data: Any, base_dir: str) -> Any:
    """
    递归解析 YAML 包含关系。

    :param data: 输入的配置数据
    :param base_dir: 基准目录
    :return: 合并包含内容后的数据
    """
    if isinstance(data, dict):
        if "include" in data:
            include_target = data.pop("include")
            targets = [include_target] if isinstance(include_target, str) else include_target
            if isinstance(targets, list):
                for t in targets:
                    abs_include = os.path.join(base_dir, t)
                    if os.path.exists(abs_include):
                        try:
                            with open(abs_include, 'r', encoding='utf-8') as f:
                                included_data = yaml.safe_load(f) or {}
                            included_data = resolve_includes(included_data, os.path.dirname(abs_include))
                            data = deep_update(included_data, data)
                        except Exception as e:
                            tlog.warning(f"⚠️ 配置文件包含失败 [{t}]: {e}")
        for k, v in data.items():
            data[k] = resolve_includes(v, base_dir)
    elif isinstance(data, list):
        return [resolve_includes(item, base_dir) for item in data]
    return data
