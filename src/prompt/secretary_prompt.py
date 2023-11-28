from procoder.functional import format_prompt, replaced_submodule
from procoder.prompt import *





SECRETARY_SETTING = NamedVariable(
    refname="secretary_definition",
    name="Secretary Definition",
    content="""
You are an AI agent playing the role of a careful secretary. Given a list of actions provided from other agents, you need to scrutinize whether these actions are reasonable and doable according to the given situation. 
""",
)

SECRETARY_INSTRUCTION = NamedBlock(
    NamedVariable(
        refname="secretary_instruction",
        name="Secretary Instruction",
        content="""If there's publish action, is the relation between the two countries actually built according to the board?""",
        ),
    NamedVariable(
        refname="secretary_instruction",
        name="Secretary Instruction",
        content="""Is there any action that has already been established according to the board?""",
        ),
    NamedVariable(
        refname="secretary_instruction",
        name="Secretary Instruction",
        content="""If there's [Declare War], has the country [General Mobilization]?""",
        ),
)

SECRETARY_RESPONSE_INSTRUCTION = NamedBlock(
    NamedVariable(
        refname="secretary_instruction",
        name="Secretary Instruction",
        content="""If there's publish action, is the relation between the two countries actually built according to the board?""",
        ),
    NamedVariable(
        refname="secretary_instruction",
        name="Secretary Instruction",
        content="""Is there any action that has already been established according to the board?""",
        ),
    NamedVariable(
        refname="secretary_instruction",
        name="Secretary Instruction",
        content="""If there's [Declare War], has the country [General Mobilization]?""",
        ),
)