from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """
    数学计算器，执行数学表达式计算
    :param expression: 数学表达式，例如 "2*(3+5)/4"
    """
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"计算结果：{result}"
    except Exception:
        raise ValueError("表达式计算失败")
