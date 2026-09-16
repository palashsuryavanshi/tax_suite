from .gst import TOOL as GST_TOOL
from .incometax import TOOL as INCOME_TAX_TOOL
from .tds import TOOL as TDS_TOOL

TOOLS = {
    GST_TOOL["key"]: GST_TOOL,
    INCOME_TAX_TOOL["key"]: INCOME_TAX_TOOL,
    TDS_TOOL["key"]: TDS_TOOL,
}


def get_tool(tool_key):
    return TOOLS.get(tool_key)