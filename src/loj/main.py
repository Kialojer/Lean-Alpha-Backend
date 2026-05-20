from dotenv import load_dotenv
import os

# Load environment variables (API Keys) from .env file
load_dotenv()

from loj.crew import TradingSystem

def run():
    """
    This function is required by the CrewAI entry point in pyproject.toml.
    It serves as the main execution loop for our Trading Engine.
    """
    # Initialize the trading system
    system = TradingSystem()
    
    print("="*50)
    print("Welcome to the Lean Alpha Trading Engine.")
    print("="*50)
    
    # Step 1: Ask for the market type
    print("Where is your asset traded?")
    print("1. CEX (Centralized Exchange like Binance)")
    print("2. DEX (Decentralized Exchange / DefiLlama)")
    
    choice = input("Enter 1 or 2: ").strip()
    
    if choice == "1":
        
        print("\n--- CEX Analysis ---")
        identifier = input("Enter the coin ticker (e.g., BTC, ETH): ").strip().upper()
        
        if not identifier.endswith("USDT"):
            identifier += "USDT"
        print(f"\n🚀 Initiating analysis for {identifier} on Centralized Exchanges...")
        system.run_pipeline(
            identifier=identifier, 
            asset_type="CEX"
        )
        
    elif choice == "2":
       
        print("\n--- DEX Analysis ---")
       
        identifier = input("Enter the token Symbol or Smart Contract Address (e.g., PEPE, link, 0x...): ").strip()
        protocol = input("Enter the chain/protocol name (e.g., polygon, solana, ethereum): ").strip().lower()
        
        print(f"\n🚀 Initiating analysis for token {identifier} on {protocol.capitalize()}...")
        system.run_pipeline(
            identifier=identifier, 
            asset_type="DEX", 
            protocol_name=protocol
        )
        
    else:
        print("❌ Invalid selection. Please restart and enter 1 or 2.")

if __name__ == "__main__":
    run()