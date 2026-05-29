import inspect
import json
import logging
from typing import Dict, List, Optional, Type, Any
from core.adapters.ai.tool_protocol import IllacmeTool

logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    🏢 [V75.0] Illacme Plenipes Global Tool Registry
    负责集中注册、查找和校验所有的工具契约。
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._instance._tools: Dict[str, Type[IllacmeTool]] = {}
            cls._instance._tool_instances: Dict[str, IllacmeTool] = {}
        return cls._instance

    def register(self, tool_class: Type[IllacmeTool]):
        """
        注册一个继承自 IllacmeTool 的工具类。
        """
        tool_name = tool_class.name
        self._tools[tool_name] = tool_class
        # 预实例化（如果工具是无状态的）
        try:
            self._tool_instances[tool_name] = tool_class()
            logger.info(f"🛠️ Tool registered: {tool_name}")
        except Exception as e:
            logger.error(f"❌ Failed to instantiate tool {tool_name}: {e}")

    def get_tool(self, tool_name: str) -> Optional[IllacmeTool]:
        """
        根据工具名获取预实例化的工具对象。
        """
        return self._tool_instances.get(tool_name)

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        安全地路由并执行对应的工具，捕获异常并返回结果字符串。
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found in registry."
            
        try:
            # 执行工具的 execute 方法
            result = tool.execute(**arguments)
            # 确保返回字符串
            if not isinstance(result, str):
                result = json.dumps(result, ensure_ascii=False)
            return result
        except Exception as e:
            logger.exception(f"Tool execution failed for {tool_name}")
            return f"Error executing tool '{tool_name}': {str(e)}"
            
    def export_all_schemas(self) -> List[Dict[str, Any]]:
        """
        导出注册表中所有工具的 OpenAI 兼容 schema，用于注入到 PayloadManager。
        """
        schemas = []
        for tool_name, tool_instance in self._tool_instances.items():
            schemas.append({
                "type": "function",
                "function": tool_instance.to_openai_schema()
            })
        return schemas
