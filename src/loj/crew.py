import json
import os
import yaml
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from loj.tools.market_tools import build_market_payload

class JudgeOutput(BaseModel):
    asset: str = Field(description="Name or symbol of the crypto asset")
    action: str = Field(description="Execution command: 'BUY' (Long) or 'SELL' (Short)")
    allocation_pct: int = Field(description="Percentage of portfolio to risk (e.g., 5, 10, 20)")
    leverage: int = Field(description="Leverage multiplier to use for the trade (e.g., 3, 5)")
    score: int = Field(description="Conviction score from 0 to 100")
    trend_bias: str = Field(description="Bullish or Bearish")
    current_price: float = Field(description="The EXACT current market price fetched from the payload")
    entry_price: float = Field(description="Suggested entry price (must be close to current_price)")
    stop_loss: float = Field(description="Strict stop loss level")
    take_profit: float = Field(description="Take profit level")
    rationale: str = Field(description="A detailed explanation citing SPECIFIC METRICS to justify the trade.")

class TradingSystem:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        agents_path = os.path.join(current_dir, 'config', 'agents.yaml')
        tasks_path = os.path.join(current_dir, 'config', 'tasks.yaml')

        with open(agents_path, 'r', encoding='utf-8') as f:
            self.agents_config = yaml.safe_load(f)
            
        with open(tasks_path, 'r', encoding='utf-8') as f:
            self.tasks_config = yaml.safe_load(f)
            
        self.gpt_mini = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        self.judge_agent = Agent(
            role=self.agents_config["quant_judge"]["role"],
            goal=self.agents_config["quant_judge"]["goal"],
            backstory=self.agents_config["quant_judge"]["backstory"],
            llm=self.gpt_mini,
            verbose=False
        )
        
        self.narrator_agent = Agent(
            role=self.agents_config["narrator"]["role"],
            goal=self.agents_config["narrator"]["goal"],
            backstory=self.agents_config["narrator"]["backstory"],
            llm=self.gpt_mini,
            verbose=False
        )

    def run_pipeline(self, identifier: str, asset_type: str = "CEX", protocol_name: str = None):
        """Executes the dual-agent workflow silently and returns data."""
        
        market_data = build_market_payload(identifier, asset_type, protocol_name)
        
        judge_task = Task(
            description=self.tasks_config["judge_task"]["description"].format(symbol=identifier, market_data=json.dumps(market_data)),
            expected_output=self.tasks_config["judge_task"]["expected_output"],
            agent=self.judge_agent,
            output_json=JudgeOutput
        )
        
        judge_crew = Crew(agents=[self.judge_agent], tasks=[judge_task], verbose=False)
        judge_result = judge_crew.kickoff()
        
        try:
            result_dict = json.loads(judge_result.raw)
        except json.JSONDecodeError:
            result_dict = {"raw_output": judge_result.raw}

        narrate_task = Task(
            description=self.tasks_config["narrate_task"]["description"].format(judge_output=json.dumps(result_dict)),
            expected_output=self.tasks_config["narrate_task"]["expected_output"],
            agent=self.narrator_agent
        )
        
        narrator_crew = Crew(agents=[self.narrator_agent], tasks=[narrate_task], verbose=False)
        final_tweet = narrator_crew.kickoff()
        
        return {
            "signal": judge_result.raw,
            "tweet": final_tweet.raw
        }