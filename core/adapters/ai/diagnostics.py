# -*- coding: utf-8 -*-
"""
🛡️ [V74.9] AI Translator Diagnostics Delegate
职责：承担 AI 算力适配器的连接与感应异常智能诊断，生成友好且易懂的排错提示。
"""

def diagnose_error_impl(translator, exception: Exception) -> str:
    """智能诊断异常，生成对用户极其友好且易懂的排错指南"""
    err_str = str(exception)
    
    # 1. 认证与权限失败
    if "401" in err_str or "unauthorized" in err_str.lower() or "invalid_api_key" in err_str.lower():
        api_key = getattr(translator.config, "api_key", None)
        if not api_key:
            return "❌ 认证失败：未填写 API Key 物理密钥。请检查并填入密钥。"
        return "❌ 认证失败：请核对填写的 API Key 物理密钥是否正确且有效。"
        
    if "400" in err_str:
        if any(x in err_str.lower() for x in ["key", "api_key", "invalid", "api key"]):
            return "❌ 认证失败：请核对填写的 API Key 物理密钥是否正确且有效 (HTTP 400)。"
        return "❌ 请求参数错误 (HTTP 400)：请检查所选的协议驱动、端点地址 (Endpoint) 或模型标识是否完全匹配。"
        
    if "403" in err_str or "forbidden" in err_str.lower():
        return "❌ 访问被拒绝 (HTTP 403)：请检查您的账户余额、API Key 权限范围或目标服务商的地区访问控制限制 (如部分地区限制访问)。"
        
    # 2. 接口路径错误 (404)
    if "404" in err_str:
        return "❌ 端点路径错误 (HTTP 404)：请核对端点地址 (Endpoint) 文本框，多写或少写了路径后缀 (例如 /v1 或 /v1beta)。"
        
    # 3. 连接拒绝
    if "refused" in err_str.lower() or "connection refused" in err_str.lower():
        return "❌ 物理连接被拒绝：目标端点物理不可达。请检查本地网络、代理工具设置，或检查目标算力服务是否正常启动。"
        
    # 4. 网络超时
    if "timeout" in err_str.lower() or "timed out" in err_str.lower():
        return "❌ 网络握手超时：与目标端点握手失败。请检查网络状态、翻墙代理工具，或检查目标服务是否响应迟缓。"
        
    # 5. 保底返回
    return f"❌ 连接异常: {err_str[:80]}..." if len(err_str) > 80 else f"❌ 连接异常: {err_str}"
