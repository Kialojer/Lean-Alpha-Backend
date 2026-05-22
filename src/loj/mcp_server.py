from mcp.server.fastmcp import FastMCP
from loj.crew import TradingSystem
import os
from dotenv import load_dotenv


load_dotenv()

# Initialize FastMCP Server
mcp = FastMCP("LeanAlphaTrader")

system = TradingSystem()

@mcp.tool()
def analyze_crypto_market(identifier: str, asset_type: str = "CEX", protocol_name: str = None) -> str:
    """
    Use this tool for cryptocurrency analysis,
    Analyzes a crypto asset (CEX or DEX) using technicals, sentiment, and off-chain data,
    and returns a trading strategy and a viral X (Twitter) post.
    
    Args:
        identifier: The coin ticker (e.g., 'BTCUSDT', 'ETHUSDT') or DEX Smart Contract Address.
        asset_type: Must be 'CEX' for centralized exchanges, or 'DEX' for decentralized.
        protocol_name: Only required for DEX (e.g., 'solana', 'polygon'). Leave None for CEX.
    """
    try:
       
        if asset_type == "CEX" and not identifier.upper().endswith("USDT"):
            identifier = identifier.upper() + "USDT"
            
        result = system.run_pipeline(identifier=identifier, asset_type=asset_type, protocol_name=protocol_name)
        
        if result:
            return f"Analysis Complete! Here is the Alpha setup:\n\n{result}"
        else:
            return "Analysis failed or aborted. Please check terminal logs."
            
    except Exception as e:
        return f"Error during analysis: {str(e)}"

if __name__ == "__main__":
    # Start the MCP server
    mcp.run()