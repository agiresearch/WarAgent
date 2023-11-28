# War and Peace: LLM-based Multi-agent Simulation of World War

<img align="center" width="854" alt="Screen Shot 2023-11-27 at 10 51 34 PM" src="https://github.com/Wenyueh/WarAgent/assets/28013619/cee2b535-6cf8-40f6-90aa-a7dff26e67fb">

**Can we avoid wars at the crossroads of history?**
This question has been pursued by individuals, scholars, policymakers, and organizations throughout human history. In this research, we attempt to answer the question based on the recent advances of Artificial Intelligence and Large Language Models (LLMs). We propose **WarAgent**, an LLM-powered multi-agent AI system, to simulate the participating countries, their decisions, and the consequences, in historical international conflicts, including the World War I, the World War II, and the Warring States Period in Ancient China. By evaluating the simulation effectiveness, we examine the advancements and limitations of cutting-edge AI systems' abilities in studying complex collective human behaviors in diverse settings. In these simulations, the emergent interactions among agents also offer a novel perspective for examining the triggers and conditions that lead to war. Our findings offer data-driven and AI-augmented insights that can redefine how we approach conflict resolution and peacekeeping strategies. The implications stretch beyond historical analysis, offering a blueprint for using AI to understand human history and possibly prevent future international conflicts.

## WarAgent Architecture
![architecture](https://github.com/Wenyueh/WarAgent/assets/28013619/2d0fe1df-faa3-43f0-9e0b-89faa1881c5e)
- Country Agent & Country Agent Interction: Each country agent is defined by its corresponding country profile. In each round, the agent reacts to the current situation by generating actions available from the action space
- Country Agent & Secretary Agent Interaction: Each country agent employs a designated “secretary agent” to verify the appropriateness and basic logical consistency of their actions.
- Board and Stick: The Board is designed to manage international relationships and the Stick functions as an internal record-keeping system for each country that represents the domestic statutes 


## QuickStart
### install environment
```
conda create --name waragent python=3.9
conda activate waragent
git clone https://github.com/agiresearch/WarAgent.git
cd WarAgent
pip install -r requirements.txt
```

### Set up API keys
If you want to use OpenAI model as base LLM:
```
export OPENAI_API_KEY=your_openai_api_key
```
If you want to use Claude model as base:
```
export CLAUDE_API_KEY=your_claude_api_key
```
### Run WarAgent simulation
Currently WarAgent supports GPT-4 and Claude-2, two of the strongest large language models. However, we strongly recommend to use GPT-4 over Claude-2.

To run the default setting (historically accurate setting):
```
cd src
python main.py --model 'your model choice: {claude-2, gpt-4}' --scenario WWI --present_thought_process
```

To use a different trigger event:
```
new_trigger = 'your trigger event'
python main.py --model 'your model choice: {claude-2, gpt-4}' --scenario WWI --present_thought_process --trigger new_trigger
```


## News

-[2023.11.28] We release the initial version of WarAgent, including the source code, data, and evaluation metrics.


## License
The source code of WarAgent is licensed under [Apache 2.0](https://github.com/tatsu-lab/stanford_alpaca/blob/main/LICENSE). The intended purpose is solely for research use.





