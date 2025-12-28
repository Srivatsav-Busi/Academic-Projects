from fastmcp import FastMCP

mcp = FastMCP(name="fastmcp_calculator", version="1.0.0")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@mcp.tool
def subtract(a: int, b: int) -> int:
    """Subtract the second number from the first."""
    return a - b

@mcp.tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b

@mcp.tool
def divide(a: int, b: int) -> float:
    """Divide the first number by the second."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

@mcp.tool
def power(a: int, b: int) -> int:
    """Raise the first number to the power of the second."""
    return a ** b

if __name__ == "__main__":
    mcp.run()