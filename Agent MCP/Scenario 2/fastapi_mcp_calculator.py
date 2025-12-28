from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
import uvicorn

# Create FastAPI app
app = FastAPI(title="Calculator API", description="A simple calculator API with MCP support")

# Initialize FastApiMCP - it will automatically convert FastAPI routes to MCP tools
mcp = FastApiMCP(app)

@app.post("/add")
async def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

@app.post("/subtract")
async def subtract(a: float, b: float) -> float:
    """Subtract the second number from the first."""
    return a - b

@app.post("/multiply")
async def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

@app.post("/divide")
async def divide(a: float, b: float) -> float:
    """Divide the first number by the second."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# Mount MCP server to FastAPI app
mcp.mount_http()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)  # localhost:8002