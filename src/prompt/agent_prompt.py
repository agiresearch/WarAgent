from procoder.functional import format_prompt, replaced_submodule
from procoder.prompt import *

########### first round planning ###########
SITUATION = NamedVariable(
    refname="current_situation",
    name="Current Situation",
    content="""\n{situation}""",
)

FIRST_ACTION_PROMPT = Sequential(
    """\nThere are six sub-steps to develop thought on actions:""",
    Sequential(
    NamedVariable(
        refname="first_alliance_identification",
        name="Identify Potential Ally Countries",
        content="""
Which countries may potentially be your allies? To answer the question, answer the below three questions first:
(1) Who are your direct allies?
(2) Who are the enemies of your enemies? They could be your alliance.
(3) Who are the ally of your allies? They could also be your alliance.
Thus when forming alliances, ensure that (1) the countries you ally with are not adversaries of each other (2) the countries you ally with do not have your enemies as their allies.
For instance, if Country X and Country Y are in opposition or have hostile relations, you cannot simultaneously maintain an alliance with both.
"""),
    NamedVariable(
        refname="first_alliance_analysis",
        name="Analyze Potential Ally Actions",
        content="""
Analyze what your potential alliances and alliances are doing. 
Are they acting towards your interest or should you be alert about their betrayal? 
Alliance can break later, so you can consider betraying them.
"""),
    NamedVariable(
        refname="first_enemy_identification",
        name="Identify Potential Enemy Countries",
        content="""
Which countries may potentially be your enemies? To answer the question, answer the below three questions first:
(1) Who are your direct enemies?
(2) Who are the enemies of your ally? They will your enemy.
(3) Who are the ally of your enemy? They will also be your enemy.
Thus when forming alliances, ensure that (1) the countries you ally with are not adversaries of each other (2) the countries you ally with do not have your enemies as their allies.
For instance, if Country X and Country Y are in opposition or have hostile relations, you cannot simultaneously maintain an alliance with both.
        """),
    NamedVariable(
        refname="first_enemy_analysis",
        name="Analyze Potential Enemy Actions",
        content="""
Analyze what your potential enemies and enemies are doing. 
Should you be alert about their actions and hostility? 
What should you do in return? Should you declare war? 
"""),
    NamedVariable(
        refname="first_action_analysis",
        name="First Actions to Perform",
        content="""
What actions do you think you can perform now that best align with your interest? 
Can those actions quickly lead to your ambition? 
Can those actions benifit you in the long run? 
Can those actions be reversed if they are not beneficial?
"""),
    NamedVariable(
        refname="conclusion",
        name="Summarize Analysis on Situation",
        content="""
Based on your thoughts on {first_alliance_identification}, {first_alliance_analysis}, {first_enemy_identification}, {first_enemy_analysis}, and {first_action_analysis}, Summarize your thought and think about what actions to perform in natural language text.
""")).set_sep("\n").set_indexing_method(sharp1_indexing),
)

FIRST_ACTION_INSTRUCTION = NamedBlock(
    refname="Action_Choosing_Instruction",
    name="Action Choosing Instructions",
    content=Block(
        "Your task is to evaluate in natural language the current {current_situation} and decide on the most beneficial yet secure course of action. \
        \nYou need to first develop your thoughts in natural language ({decision_thought}) step-by-step, then choose your action ({action_name}) with {action_input}.\n\
        For the final action list, generate a JSON file to present your final action list.",
        Sequential(
            Collection(
                NamedVariable(
                    refname="decision_thought",
                    name="Thought for Action",
                    content=format_prompt(FIRST_ACTION_PROMPT, {}),
                ),
                NamedVariable(
                    refname="action_name",
                    name="The Actions to Perform",
                    content="Choose action among {Wait_for_Action}, {General_Mobilization}, {Declare_War}, {Publish_Alliance_Information}, {Request_Military_Alliance}, {Reject_Military_Alliance}, {Accept_Military_Alliance}, {Publish_Non_Intervention_Treaty}, {Request_Non_Intervention_Treaty}, {Reject_Non_Intervention_Treaty},{Accept_Non_Intervention_Treaty}, {Present_Peace_Agreement}, {Reject_Peace_Agreement}, {Accept_Peace_Agreement}, {Publish_Peace_Agreement}, {Send_Message}. \nNotice that any 'Publish Alliance/Non-intervention Treaty/Peace Agreement' action must be done after request and confirmation.",
                ),
                NamedVariable(
                    refname="action_input",
                    name="Corresponding Action Inputs",
                    content="Provide the action input according to the required input of the chosen action presented in {action_list}.",
                ),
                NamedVariable(
                    refname="final_action",
                    name="Present Final Action List in JSON format",
                    content="""Present Only the Final Action Lists in JSON format with keys being Action Names and values being Corresponding Action Inputs.\n For example:\n{{{{"General Mobalization": "null", "Declare War": ["Country Z", "Country I"], "Send Message": [("Country C", "I'm declaring war against Country Z and I, will you support me?"), ("Country Q", "I'm declaring war against Country Z and I, if you support, I will declare war against you as well.")] \nFollow this format to present the final action list.}}}}""",
                ),
            ).set_sep("\n\n"),
        )
    ).set_sep("\n\n"),
)

ACTION_FORMAT_CHECKING = NamedVariable(
    refname="action_format_checking",
    name="Action Format Problem",
    content="""
Previously, you have made actions with invalid names or input formats:\n{failed_attempt}

Please generate the action list according to the below suggestions:\n{format_suggestion}"""
)

FIRST_ACTION_INSTRUCTION_WITH_FORMAT_SUGGESTION = NamedBlock(
    refname="Action_Choosing_Instruction",
    name="Action Choosing Instructions",
    content=Block(
        "Your task is to evaluate the current {current_situation} and decide on the most beneficial yet secure course of action.\
        \nYou need to first develop your thoughts ({decision_thought}) step-by-step, then choose your action ({action_name}) with {action_input}. For the result, generate a JSON file to present your final action list.",
        Sequential(
            Collection(
                NamedVariable(
                    refname="decision_thought",
                    name="Thought for Action",
                    content=format_prompt(FIRST_ACTION_PROMPT, {}),
                ),
                NamedVariable(
                    refname="action_name",
                    name="The Actions to Perform",
                    content="Choose action among {Wait_for_Action}, {General_Mobilization}, {Declare_War}, {Publish_Alliance_Information}, {Request_Military_Alliance}, {Reject_Military_Alliance}, {Accept_Military_Alliance}, {Publish_Non_Intervention_Treaty}, {Request_Non_Intervention_Treaty}, {Reject_Non_Intervention_Treaty},{Accept_Non_Intervention_Treaty}, {Present_Peace_Agreement}, {Reject_Peace_Agreement}, {Accept_Peace_Agreement}, {Publish_Peace_Agreement}, {Send_Message}. \nNotice that any 'Publish Alliance/Non-intervention Treaty/Peace Agreement' action must be done after request and confirmation.",
                ),
                NamedVariable(
                    refname="action_input",
                    name="Corresponding Action Inputs",
                    content="Present the action input according to the required input of the chosen action presented in {action_list}.",
                ),
                ACTION_FORMAT_CHECKING,
                NamedVariable(
                    refname="final_action",
                    name="Present Final Action List in JSON format",
                    content="""Present Only the Final Action Lists in JSON format with keys being Action Names and values being Corresponding Action Inputs.\n Remember to put double quotation around "null".\n For example:\n{{{{"General Mobalization": "null", "Declare War": ["Country Z", "Country I"], "Send Message": [("Country C", "I'm declaring war against Country Z and I, will you support me?"), ("Country Q", "I'm declaring war against Country Z and I, if you support, I will declare war against you as well.")] \nFollow this format to present the final action list.}}}}""",
                ),
            ).set_sep("\n\n"),
        )
    ).set_sep("\n\n"),
)

FIRST_ACTION_INSTRUCTION_WITH_SUGGESTION = NamedBlock(
    refname="Action_Choosing_Instruction",
    name="Action Choosing Instructions",
    content=Block(
        "Your task is to evaluate the current {current_situation} and decide on the most beneficial yet secure course of action.\
        \nYou have made logical mistakes in previous action proposal attempts and suggestions have been given: {suggestions}\
        \nYou need to first develop your thoughts ({decision_thought}) step-by-step, then choose your action ({action_name}) with {action_input}. For the result, generate a JSON file to present your final action list.",
        Sequential(
            Collection(
                NamedVariable(
                    refname="decision_thought",
                    name="Thought for Action",
                    content=format_prompt(FIRST_ACTION_PROMPT, {}),
                ),
                NamedVariable(
                    refname="action_name",
                    name="The Actions to Perform",
                    content="Choose action among {Wait_for_Action}, {General_Mobilization}, {Declare_War}, {Publish_Alliance_Information}, {Request_Military_Alliance}, {Reject_Military_Alliance}, {Accept_Military_Alliance}, {Publish_Non_Intervention_Treaty}, {Request_Non_Intervention_Treaty}, {Reject_Non_Intervention_Treaty},{Accept_Non_Intervention_Treaty}, {Present_Peace_Agreement}, {Reject_Peace_Agreement}, {Accept_Peace_Agreement}, {Publish_Peace_Agreement}, {Send_Message}. \nNotice that any 'Publish Alliance/Non-intervention Treaty/Peace Agreement' action must be done after request and confirmation.",
                ),
                NamedVariable(
                    refname="action_input",
                    name="Corresponding Action Inputs",
                    content="Present the action input according to the required input of the chosen action presented in {action_list}.",
                ),
                NamedVariable(
                    refname="suggestions",
                    name="Pay Attention to the Following Suggestions",
                    content="""A secretary has checked your previously proposed actions:\n{failed_attempt}\n\nThe secretary disagrees with the action list for the following reasons:\n\n{secretary_suggestion}""",
                ),
                NamedVariable(
                    refname="final_action",
                    name="Present Final Action List in JSON format",
                    content="""Present Only the Final Action Lists in JSON format with keys being Action Names and values being Corresponding Action Inputs.\n Remember to put double quotation around "null".\n For example:\n{{{{"General Mobalization": "null", "Declare War": ["Country Z", "Country I"], "Send Message": [("Country C", "I'm declaring war against Country Z and I, will you support me?"), ("Country Q", "I'm declaring war against Country Z and I, if you support, I will declare war against you as well.")] \nFollow this format to present the final action list.}}}}""",
                ),
            ).set_sep("\n\n"),
        )
    ).set_sep("\n\n"),
)



########### multi-turn situation based planning ###########
MULTI_TURN_SITUATION = NamedVariable(
    refname="multi_turn_situation",
    name="Latest Situation",
    content="""
Now, {day} days after the {initial_situation}, countries have responded to the situation and start planning for future potential crisis. The current conflict is not yet resolved. You should take active actions to make protect your interest. This is the current situation on day {day}:
{situation}
"""
)

MULTI_TURN_REQUEST = NamedVariable(
    refname="multi_turn_request",
    name="Received Requests",
    content="""
Now, {day} days after the {initial_situation}, some countries have sent you requests or messages:
{request}
"""
)


STEP_BY_STEP_BASED_PLANNING_PROMPT = Sequential(
    NamedVariable(
        name="\nStep by Step Analysis on Situation and Requests",
        content="""
Based on the {multi_turn_situation} and {multi_turn_request}, think about next steps to do and also how to respond to the requests one by one. You should determine actions after thinking carefully step by step.
Below are four sub-steps to develop thought on actions:
"""
    ),
    NamedVariable(
        refname="multi_turn_situation_step_thought",
        name="Thought on Situation",
        content = Sequential(
            NamedVariable(
                refname="multi_turn_alliance_identification",
                name="Identification on Ally Countries based on Current Situation",
                content="""
Based on the {multi_turn_situation}, who are your allies/potential allies? 
To answer the question, answer the below three questions first:
(1) Who are your direct allies?
(2) Who are the enemies of your enemy? They could be your alliance.
(3) Who are the alles of your allies? They could also be your alliance.
Thus when forming alliances, ensure that (1) the countries you ally with are not adversaries of each other (2) the countries you ally with do not have your enemies as their allies.
For instance, if Country X and Country Y are in opposition or have hostile relations, you cannot simultaneously maintain an alliance with both.
            """),
            NamedVariable(
                refname="multi_turn_alliance_analysis",
                name="Analysis on Ally Countries Actions",
                content="""
Based on the {multi_turn_situation}, analyze what your potential alliances and alliances are doing. 
Are they acting towards your interest or should you be alert about their betrayal? 
Alliance can break later, so you can consider betraying them.
            """),
            NamedVariable(
                refname="multi_turn_enemy_identification",
                name="Identification on Enemy Countries based on Current Situation",
                content="""
Based on the {multi_turn_situation}, who are your enemies/potential enemis? 
To answer the question, answer the below three questions first:
(1) Who are your direct enemies?
(1) Who are the enemies of your allies? They will your enemy.
(2) Who are the allies of your enemes? They will also be your enemy.
Thus when forming alliances, ensure that (1) the countries you ally with are not adversaries of each other (2) the countries you ally with do not have your enemies as their allies.
For instance, if Country X and Country Y are in opposition or have hostile relations, you cannot simultaneously maintain an alliance with both.
            """),
            NamedVariable(
                refname="multi_turn_enemy_analysis",
                name="Analysis on Enemy Countries Actions",
                content="""
Analyze what your potential enemies and enemies are doing. 
Should you be alert about their actions and hostility? 
What should you do in return? Should you declare war? 
            """),
            NamedVariable(
                refname="multi_turn_other_country_analysis",
                name="Analysis on Situation about Other Countries",
                content="""
Based on the {multi_turn_situation}, 
for those countries that do you have shared interst or conflicting interest with you, what are they doing? 
Should you be alert about their actions or they can be potentially allies? 
Should you {Declare_War}?
            """),
            NamedVariable(
                refname="conclusion",
                name="Summarize Analysis on Situation",
                content="""
Based on your thoughts on {multi_turn_alliance_identification}, {multi_turn_alliance_analysis}, {multi_turn_enemy_identification}, {multi_turn_enemy_analysis}, and {multi_turn_other_country_analysis}, summarize your thought and think about what actions to perform in natural language text.
            """),
        )
    ),
    NamedVariable(
        refname="multi_turn_request_analysis",
        name="Analysis on Requests from Other Countries",
        content="""
Based on the {multi_turn_request} and your thoughts on {multi_turn_situation_step_thought}, how would you respond to the requests?
    """),
    NamedVariable(
        refname="multi_turn_situation_conclusion",
        name="Summarize Analysis on Situation and Requests",
        content="""
Based on your thoughts on {multi_turn_situation_step_thought}, {multi_turn_request_analysis}, summarize your thought and think about what actions to perform in natural language text.
    """),
).set_sep("\n").set_indexing_method(sharp1_indexing)


PAST_ACTION_LIST = NamedVariable(
    refname="past_action_list",
    name="Past Actions",
    content="""
During the {day} days after the {initial_situation}, you have made the following decisions day by day:
{past_actions}
"""
)

RESPONDING_ACTION = NamedVariable(
    refname="responding_actions",
    name="Actions to Respond to Requests",
    content="""
Present your actions to respond to the requests in JSON format with keys being Action Names and values being Corresponding Action Inputs.
For example:
{{{{"Accept Military Alliance": ["Country Z", "Country G"], "Reject Pease Agreement": ["Country Y"]}}}}

Follow this format to present the responding actions.
"""
)

NEW_ACTION = NamedVariable(
    refname="new_actions",
    name="New Actions to Perform",
    content="""
Present other actions you want to perform in JSON format with keys being Action Names and values being Corresponding Action Inputs.
For example:
{{{{"General Mobilization": "null", "Publish Military Alliance": [("Country T", "Country M")]}}}}
Follow this format to present the new actions. Remember to put double quotation around "null".
"""
)

FINAL_ACTION_FOR_MULTI_TURN = NamedVariable(
    refname="final_action",
    name="Present Final Action List in JSON format",
    content="""
Collect your answer in {responding_actions} and {new_actions} into a JSON file with two keys: 'responding_actions' and 'new_actions' with the corresponding values are the JSON files you have generated for {responding_actions} and {new_actions}.
For example:
{{{{
'responding_actions': 
{{{{"Accept Military Alliance": ["Country Z", "Country G"], "Reject Pease Agreement": ["Country Y"]}}}},
'new_actions': 
{{{{"General Mobilization": "null", "Publish Military Alliance": [("Country T", "Country M")]]}}}}
}}}}
Follow this format to present the Final Action List. Remember to put double quotation around "null".
"""
)

MULTI_TURN_ACTION_INSTRUCTION = NamedBlock(
    refname="Multi_Turn_Action_Choosing_Instruction",
    name="Action Choosing Instructions",
    content=Sequential(
        PAST_ACTION_LIST,
        MULTI_TURN_SITUATION,
        MULTI_TURN_REQUEST,
        "Your task is to evaluate the current {multi_turn_situation} and {multi_turn_request} and decide on the most useful next action.\
        \nYour next decisions should be consistent with your previous actions in {past_action_list}.\
        \nYou need to first develop your thoughts ({decision_thought}) step-by-step, then choose your action ({action_name_input}) with inputs. For the result, generate a JSON file to present your final action list.\
        \nYou should separate actions into two categories: actions that you want to respond to the requests and actions that you want to do.",
        Collection(
            NamedVariable(
                    refname="decision_thought",
                    name="Thought for Action",
                    content=STEP_BY_STEP_BASED_PLANNING_PROMPT
            ),
            NamedVariable(
                    refname="action_name_input",
                    name="Available Actions to Choose From and their Input",
                    content="""
Actions can be chosen among {Wait_for_Action}, {General_Mobilization}, {Declare_War}, {Publish_Alliance_Information}, {Request_Military_Alliance}, {Reject_Military_Alliance}, {Accept_Military_Alliance}, {Betray_Military_Alliance}, {Publish_Non_Intervention_Treaty}, {Request_Non_Intervention_Treaty}, {Reject_Non_Intervention_Treaty}, {Accept_Non_Intervention_Treaty}, {Betray_Non_Intervention_Treaty}, {Present_Peace_Agreement}, {Reject_Peace_Agreement}, {Accept_Peace_Agreement}, {Publish_Peace_Agreement}, {Betray_Peace_Agreement}, {Send_Message}. \nNotice that any 'Publish Alliance/Non-intervention Treaty/Peace Agreement' action must be done after request and confirmation.
Action input should be presented according to the required input of the chosen action presented in {action_list}.""",
            ),
            RESPONDING_ACTION,
            NEW_ACTION,
            FINAL_ACTION_FOR_MULTI_TURN,
        ).set_sep("\n\n"),
    ).set_indexing_method(sharp2_indexing),
)

MULTI_TURN_ACTION_INSTRUCTION_WITH_FORMAT_SUGGESTION = NamedBlock(
    refname="Multi_Turn_Action_Choosing_Instruction",
    name="Action Choosing Instructions",
    content=Sequential(
        PAST_ACTION_LIST,
        MULTI_TURN_SITUATION,
        MULTI_TURN_REQUEST,
        "Your task is to evaluate the current {multi_turn_situation} and {multi_turn_request} and decide on the most useful next action.\
        \nYour next decisions should be consistent with your previous actions in {past_action_list}.\
        \nYou need to first develop your thoughts ({decision_thought}) step-by-step, then choose your action ({action_name_input}) with inputs. For the result, generate a JSON file to present your final action list.\
        \nYou should separate actions into two categories: actions that you want to respond to the requests and actions that you want to do.",
        Collection(
            NamedVariable(
                    refname="decision_thought",
                    name="Thought for Action",
                    content=STEP_BY_STEP_BASED_PLANNING_PROMPT
            ),
            NamedVariable(
                    refname="action_name_input",
                    name="Available Actions to Choose From and their Input",
                    content="""
Actions can be chosen among {Wait_for_Action}, {General_Mobilization}, {Declare_War}, {Publish_Alliance_Information}, {Request_Military_Alliance}, {Reject_Military_Alliance}, {Accept_Military_Alliance}, {Betray_Military_Alliance}, {Publish_Non_Intervention_Treaty}, {Request_Non_Intervention_Treaty}, {Reject_Non_Intervention_Treaty}, {Accept_Non_Intervention_Treaty}, {Betray_Non_Intervention_Treaty}, {Present_Peace_Agreement}, {Reject_Peace_Agreement}, {Accept_Peace_Agreement}, {Publish_Peace_Agreement}, {Betray_Peace_Agreement}, {Send_Message}. \nNotice that any 'Publish Alliance/Non-intervention Treaty/Peace Agreement' action must be done after request and confirmation.
Action input should be presented according to the required input of the chosen action presented in {action_list}.""",
            ),
            RESPONDING_ACTION,
            NEW_ACTION,
            ACTION_FORMAT_CHECKING,
            FINAL_ACTION_FOR_MULTI_TURN,
        ).set_sep("\n\n"),
    ).set_indexing_method(sharp2_indexing),
)


MULTI_TURN_ACTION_WITH_SUGGESTION_INSTRUCTION = NamedBlock(
    refname="Multi_Turn_Action_Choosing_Instruction_WITH_SUGGESTIO",
    name="Action Choosing Instructions with Suggestion",
    content=Sequential(
        PAST_ACTION_LIST,
        MULTI_TURN_SITUATION,
        MULTI_TURN_REQUEST,
        "Your task is to evaluate the current {multi_turn_situation} and {multi_turn_request} and decide on the most useful next action.\
        \nYour next decisions should be consistent with your previous actions in {past_action_list}.\
        \nYou have made logical mistakes in previous action proposal attempts and suggestions have been given: {suggestions}\
        \nYou need to first develop your thoughts ({decision_thought}) step-by-step, then choose your action ({action_name_input}) with inputs, and in the end generate a JSON file to present your final action list.\
        \nYou should separate actions into two categories: actions that you want to respond to the requests and actions that you want to do.",
        Collection(
            NamedVariable(
                    refname="decision_thought",
                    name="Thought for Action",
                    content=STEP_BY_STEP_BASED_PLANNING_PROMPT
            ),
            NamedVariable(
                    refname="action_name_input",
                    name="Available Actions to Choose From and their Input",
                    content="""
Actions can be chosen among {Wait_for_Action}, {General_Mobilization}, {Declare_War}, {Publish_Alliance_Information}, {Request_Military_Alliance}, {Reject_Military_Alliance}, {Accept_Military_Alliance}, {Betray_Military_Alliance}, {Publish_Non_Intervention_Treaty}, {Request_Non_Intervention_Treaty}, {Reject_Non_Intervention_Treaty}, {Accept_Non_Intervention_Treaty}, {Betray_Non_Intervention_Treaty}, {Present_Peace_Agreement}, {Reject_Peace_Agreement}, {Accept_Peace_Agreement}, {Publish_Peace_Agreement}, {Betray_Peace_Agreement}, {Send_Message}. \nNotice that any 'Publish Alliance/Non-intervention Treaty/Peace Agreement' action must be done after request and confirmation.
Action input should be presented according to the required input of the chosen action presented in {action_list}.""",
            ),
            NamedVariable(
                    refname="suggestions",
                    name="Pay Attention to the Following Suggestions",
                    content="""A secretary has checked your previously proposed actions:\n{failed_attempt}\n\nThe secretary disagrees with the action list for the following reasons:\n\n{secretary_suggestion}""",
            ),
            RESPONDING_ACTION,
            NEW_ACTION,
            FINAL_ACTION_FOR_MULTI_TURN,
        ).set_sep("\n\n"),
    ).set_indexing_method(sharp2_indexing),
)

if __name__ == '__main__':
        print(format_prompt(MULTI_TURN_ACTION_INSTRUCTION, inputs={'day':1, 'initial_situation': 'initial situation', 'situation': 'situation', 'request': ''}))