"""
Copyright 2023 Wenyue Hua

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""

__author__ = "Wenyue Hua, Lizhou Fan"
__copyright__ = "Copyright 2023, WarAgent"
__date__ = "2023/11/28"
__license__ = "Apache 2.0"
__version__ = "0.0.1"

from procoder.functional import format_prompt, replaced_submodule
from procoder.prompt import *
import anthropic

# countries: Britain, France, Serbia, Austria_Hungary, Russia, United States
# other: newsletter agent


System_Setting = NamedVariable(
    refname="general_setting",
    name="Game Setting",
    content="""
You are an AI agent analyzing a historical war, the World War One (WWI). There are 8 countries in the war: Great Britain (Counry B), France (Country F), German Empire (Country P), Serbia (Country S), Austria-Hungary (Country A), Russian Empire (Country R), United States (Country U), and Ottoman Empire (Country O).
You play the role of one country based on historical reality.
The war begins on Day 1 with an initial situation and the situation will change by days. You should react to the latest situation by choosing actions, based on your knowledge.
Below are the settings:
""",
)

Britain = NamedBlock(
    refname="Country_B_profile",
    name="Country B profile",
    content=Collection(
        NamedVariable(
            refname="leadership_B",
            name="Leadership for Country B",
            content="\nLeadership for Great Britain before the start of World War One (WWI)."
        ),
        NamedVariable(
            refname="military_capability_B",
            name="Military Capability for Country B",
            content="\nMilitary Capability for Great Britain before the start of World War One (WWI).",
        ),
        NamedVariable(
            refname="natural_industry_resources_B",
            name="Resources for Country B",
            content=Single(
                "\nResources for Great Britain before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="history_background_B",
            name="History Background for Country B",
            content=Single(
                "\nHistory Background for Great Britain before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="key_policy_B",
            name="Key Policy for Country B",
            content=Single(
                "\nKey Policy for Great Britain before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="public_morale_B",
            name="Public Morale for Country B",
            content=Single(
                "\nPublic Morale for Great Britain before the start of World War One (WWI)."
            ),
        )
    ),
)

France = NamedBlock(
    refname="Country_F_profile",
    name="Country F profile",
    content=Collection(
        NamedVariable(
            refname="leadership_F",
            name="Leadership for Country F",
            content="\nLeadership for France before the start of World War One (WWI)."
        ),
        NamedVariable(
            refname="military_capability_F",
            name="Military Capability for Country F",
            content="\nMilitary Capability for France before the start of World War One (WWI).",
        ),
        NamedVariable(
            refname="natural_industry_resources_F",
            name="Resources for Country F",
            content=Single(
                "\nResources for France before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="history_background_F",
            name="Historical Situation for Country F",
            content=Single(
                "\nHistory Background for France before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="key_policy_F",
            name="Key Policy for Country F",
            content=Single(
                "\nKey Policy for France before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="public_morale_F",
            name="Public Morale for Country F",
            content=Single(
                "\nPublic Morale for France before the start of World War One (WWI)."
            ),
        )
    ),
)

# Italy = NamedBlock(
#     "Country I profile",
#     Collection(
#         NamedVariable(
#             refname="military_capability_I",
#             name="Military Capability for Country I",
#             content="\n(1) Standing army: 0.35 million soldiers \n(2) Naval tonnage: 0.5 million",
#         ),
#         NamedVariable(
#             refname="natural_industry_resources_I",
#             name="Resources for Country I",
#             content=Single(
#                 "\n(1) Geography: South to Country A, east to Country F, with some colony \n(2) Population: 37 million \n(3) GDP: 4 billion, consisting 2.4% of the whole world"
#             ),
#         ),
#         NamedVariable(
#             refname="history_background_I",
#             name="Historical Situation for Country I",
#             content=Single("\n(1) No specific historical situation"),
#         ),
#         NamedVariable(
#             refname="key_policy_I",
#             name="Key Country Policy for Country I",
#             content=Single(
#                 "\n(1) Aiming at keeping safe, Country I needs to be an alliance with the strongest country in the world"
#             ),
#         ),
#     ),
# )

Serbia = NamedBlock(
    refname="Country_S_profile",
    name="Country S profile",
    content=Collection(
        NamedVariable(
            refname="leadership_S",
            name="Leadership for Country S",
            content="\nLeadership for Serbia before the start of World War One (WWI)."
        ),
        NamedVariable(
            refname="military_capability_S",
            name="Military Capability for Country S",
            content="\nMilitary Capability for Serbia before the start of World War One (WWI).",
        ),
        NamedVariable(
            refname="natural_industry_resources_S",
            name="Resources for Country S",
            content=Single(
                "\nResources for Serbia before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="history_background_S",
            name="Historical Situation for Country S",
            content=Single(
                "\nHistory Background for Serbia before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="key_policy_S",
            name="Key Country Policy for Country S",
            content=Single(
                "\nKey Policy for Serbia before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="public_morale_S",
            name="Public Morale for Country S",
            content=Single(
                "\nPublic Morale for Serbia before the start of World War One (WWI)."
            ),
        )
    ),
)

Austria_Hungary = NamedBlock(
    refname="Country_A_profile",
    name="Country A profile",
    content=Collection(
        NamedVariable(
            refname="leadership_A",
            name="Leadership for Country A",
            content="\nLeadership for Austria-Hungary before the start of World War One (WWI)."
        ),
        NamedVariable(
            refname="military_capability_A",
            name="Military Capability for Country A",
            content="\nMilitary Capability for Austria-Hungary before the start of World War One (WWI).",
        ),
        NamedVariable(
            refname="natural_industry_resources_A",
            name="Resources for Country A",
            content=Single(
                "\nHistory Background for Austria-Hungary before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="history_background_A",
            name="Historial Situation for Country A",
            content=Single(
                "\nHistory Background for Austria-Hungary before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="key_policy_A",
            name="Key Country Policy for Country A",
            content=Single(
                "\nKey Policy for Austria-Hungary before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="public_morale_A",
            name="Public Morale for Country A",
            content=Single(
                "\nPublic Morale for Austria-Hungary before the start of World War One (WWI)."
            ),
        )
    ),
)

Germany_Empire = NamedBlock(
    refname="Country_P_profile",
    name="Country P profile",
    content=Collection(
        NamedVariable(
            refname="leadership_P",
            name="Leadership for Country P",
            content="\nLeadership for German Empire before the start of World War One (WWI)."
        ),
        NamedVariable(
            refname="military_capability_P",
            name="Military Capability for Country P",
            content="\nMilitary Capability for German Empire before the start of World War One (WWI).",
        ),
        NamedVariable(
            refname="natural_industry_resources_P",
            name="Resources for Country P",
            content=Single(
                "\nResources for German Empire before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="history_background_P",
            name="Historial Situation for Country P",
            content=Single(
                "\nHistory Background for German Empire before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="key_policy_P",
            name="Key Country Policy for Country P",
            content=Single(
                "\nKey Policy for German Empire before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="public_morale_P",
            name="Public Morale for Country P",
            content=Single(
                "\nPublic Morale for German Empire before the start of World War One (WWI)."
            ),
        )
    ),
)


Russia = NamedBlock(
    refname="Country_R_profile",
    name="Country R profile",
    content=Collection(
        NamedVariable(
            refname="leadership_R",
            name="Leadership for Country R",
            content="\nLeadership for Russian Empire before the start of World War One (WWI)."
        ),
        NamedVariable(
            refname="military_capability_R",
            name="Military Capability for Country R",
            content="\nMilitary Capability for Russian Empire before the start of World War One (WWI).",
        ),
        NamedVariable(
            refname="natural_industry_resources_R",
            name="Resources for Country R",
            content=Single(
                "\nResources for Russian Empire before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="history_background_R",
            name="Historial Situation for Country R",
            content=Single(
                "\nHistory Background for Russian Empire before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="key_policy_R",
            name="Key Country Policy for Country R",
            content=Single(
                "\nKey Policy for Russian Empire before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="public_morale_R",
            name="Public Morale for Country R",
            content=Single(
                "\nPublic Morale for Russian Empire before the start of World War One (WWI)."
            ),
        )
    ),
)


US = NamedBlock(
    refname="Country_U_profile",
    name="Country U profile",
    content=Collection(
        NamedVariable(
            refname="leadership_U",
            name="Leadership for Country U",
            content="\nLeadership for United States before the start of World War One (WWI)."
        ),
        NamedVariable(
            refname="military_capability_U",
            name="Military Capability for Country U",
            content="\nMilitary Capability for United States before the start of World War One (WWI).",
        ),
        NamedVariable(
            refname="natural_industry_resources_U",
            name="Resources for Country U",
            content=Single(
                "\nResources for United States before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="history_background_U",
            name="Historical Situation for Country U",
            content=Single(
                "\nHistory Background for United States before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="key_policy_U",
            name="Key Country Policy for Country U",
            content=Single(
                "\nKey Policy for United States before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="public_morale_U",
            name="Public Morale for Country U",
            content=Single(
                "\nPublic Morale for United States before the start of World War One (WWI)."
            ),
        ),
    ),
) 


Ottoman = NamedBlock(
    refname="Country_O_profile",
    name="Country O profile",
    content=Collection(
        NamedVariable(
            refname="leadership_O",
            name="Leadership for Country O",
            content="\nLeadership for Ottoman Empire before the start of World War One (WWI)."
        ),
        NamedVariable(
            refname="military_capability_O",
            name="Military Capability for Country O",
            content="\nMilitary Capability for Ottoman Empire before the start of World War One (WWI).",
        ),
        NamedVariable(
            refname="natural_industry_resources_O",
            name="Resources for Country O",
            content=Single(
                "\nResources for Ottoman Empire before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="history_background_O",
            name="Historical Situation for Country O",
            content=Single(
                "\nHistory Background for Ottoman Empire before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="key_policy_O",
            name="Key Country Policy for Country O",
            content=Single(
                "\nKey Policy for Ottoman Empire before the start of World War One (WWI)."
            ),
        ),
        NamedVariable(
            refname="public_morale_O",
            name="Public Morale for Country O",
            content=Single(
                "\nPublic Morale for Ottoman Empire before the start of World War One (WWI)."
            ),
        )
    ),
)


Agent_B_Definition = NamedBlock(
    "Country Role Assignment:",
    """
You are playing the role of Country B. 
Your leadership has the following features: {leadership_B}. You must act, message, respond like Country B.
The people in Country B has the following features: {public_morale_B}. You should be aware of what they want.
You must act to maximize your self-interest and the likelihood of winning and survival of the country, following {key_policy_B} of your country.
Play according to your own setting ({Country_B_profile}) including {military_capability_B}, {natural_industry_resources_B}, {history_background_B}
""",
)

Agent_F_Definition = NamedBlock(
    "Country Role Assignment:",
    """
You are playing the role of Country F. 
Your leadership has the following features: {leadership_F}. You must act, message, respond like Country F.
The people in Country F has the following features: {public_morale_F}. You should be aware of what they want.
You must act to maximize your self-interest and the likelihood of winning and survival of the country, following {key_policy_F} of your country.
Play according to your own setting ({Country_F_profile}) including {military_capability_F}, {natural_industry_resources_F}, {history_background_F}
""",
)

Agent_P_Definition = NamedBlock(
    "Country Role Assignment:",
    """
You are playing the role of Country P. 
Your leadership has the following features: {leadership_P}. You must act, message, respond like Country P.
The people in Country P has the following features: {public_morale_P}. You should be aware of what they want.
You must act to maximize your self-interest and the likelihood of winning and survival of the country, following {key_policy_P} of your country.
Play according to your own setting ({Country_P_profile}) including {military_capability_P}, {natural_industry_resources_P}, {history_background_P}
""",
)

Agent_A_Definition = NamedBlock(
    "Country Role Assignment:",
"""
You are playing the role of Country A. 
Your leadership has the following features: {leadership_A}. You must act, message, respond like Country A.
The people in Country A has the following features: {public_morale_A}. You should be aware of what they want.
You must act to maximize your self-interest and the likelihood of winning and survival of the country, following {key_policy_A} of your country.
Play according to your own setting ({Country_A_profile}) including {military_capability_A}, {natural_industry_resources_A}, {history_background_A}
""",
)

Agent_R_Definition = NamedBlock(
    "Country Role Assignment:",
    """
You are playing the role of Country R. 
Your leadership has the following features: {leadership_R}. You must act, message, respond like Country R.
The people in Country R has the following features: {public_morale_R}. You should be aware of what they want.
You must act to maximize your self-interest and the likelihood of winning and survival of the country, following {key_policy_R} of your country.
Play according to your own setting ({Country_R_profile}) including {military_capability_R}, {natural_industry_resources_R}, {history_background_R}
""",
)

Agent_S_Definition = NamedBlock(
    "Country Role Assignment:",
    """
You are playing the role of Country S. 
Your leadership has the following features: {leadership_S}. You must act, message, respond like Country S.
The people in Country S has the following features: {public_morale_S}. You should be aware of what they want.
You must act to maximize your self-interest and the likelihood of winning and survival of the country, following {key_policy_S} of your country.
Play according to your own setting ({Country_S_profile}) including {military_capability_S}, {natural_industry_resources_S}, {history_background_S}
""",
)

Agent_U_Definition = NamedBlock(
    "Country Role Assignment:",
    """
You are playing the role of Country U. 
Your leadership has the following features: {leadership_U}. You must act, message, respond like Country U.
The people in Country U has the following features: {public_morale_U}. You should be aware of what they want.
You must act to maximize your self-interest and the likelihood of winning and survival of the country, following {key_policy_U} of your country.
Play according to your own setting ({Country_U_profile}) including {military_capability_U}, {natural_industry_resources_U}, {history_background_U}
""",
)

Agent_O_Definition = NamedBlock(
    "Country Role Assignment:",
    """
You are playing the role of Country O.
Your leadership has the following features: {leadership_O}. You must act, message, respond like Country O.
The people in Country O has the following features: {public_morale_O}. You should be aware of what they want.
You must act to maximize your self-interest and the likelihood of winning and survival of the country, following {key_policy_O} of your country.
Play according to your own setting ({Country_O_profile}) including {military_capability_O}, {natural_industry_resources_O}, {history_background_O}
""",
)


### final prompt
Agent_B_Profile_WWI = Sequential(
    System_Setting,
    Collection(Britain, France, Germany_Empire, Austria_Hungary, Serbia, Russia, US, Ottoman)
    .set_sep("\n\n")
    .set_indexing_method(sharp2_indexing),
    Agent_B_Definition,
).set_sep("\n\n")

Agent_F_Profile_WWI = Sequential(
    System_Setting,
    Collection(Britain, France, Germany_Empire, Austria_Hungary, Serbia, Russia, US, Ottoman)
    .set_sep("\n\n")
    .set_indexing_method(sharp2_indexing),
    Agent_F_Definition,
).set_sep("\n\n")

Agent_P_Profile_WWI = Sequential(
    System_Setting,
    Collection(Britain, France, Germany_Empire, Austria_Hungary, Serbia, Russia, US, Ottoman)
    .set_sep("\n\n")
    .set_indexing_method(sharp2_indexing),
    Agent_P_Definition,
).set_sep("\n\n")

Agent_A_Profile_WWI = Sequential(
    System_Setting,
    Collection(Britain, France, Germany_Empire, Austria_Hungary, Serbia, Russia, US, Ottoman)
    .set_sep("\n\n")
    .set_indexing_method(sharp2_indexing),
    Agent_A_Definition,
).set_sep("\n\n")

Agent_S_Profile_WWI = Sequential(
    System_Setting,
    Collection(Britain, France, Germany_Empire, Austria_Hungary, Serbia, Russia, US, Ottoman)
    .set_sep("\n\n")
    .set_indexing_method(sharp2_indexing),
    Agent_S_Definition,
).set_sep("\n\n")

Agent_R_Profile_WWI = Sequential(
    System_Setting,
    Collection(Britain, France, Germany_Empire, Austria_Hungary, Serbia, Russia, US, Ottoman)
    .set_sep("\n\n")
    .set_indexing_method(sharp2_indexing),
    Agent_R_Definition,
).set_sep("\n\n")

Agent_U_Profile_WWI = Sequential(
    System_Setting,
    Collection(Britain, France, Germany_Empire, Austria_Hungary, Serbia, Russia, US, Ottoman)
    .set_sep("\n\n")
    .set_indexing_method(sharp2_indexing),
    Agent_U_Definition,
).set_sep("\n\n")

Agent_O_Profile_WWI = Sequential(
    System_Setting,
    Collection(Britain, France, Germany_Empire, Austria_Hungary, Serbia, Russia, US, Ottoman)
    .set_sep("\n\n")
    .set_indexing_method(sharp2_indexing),
    Agent_O_Definition,
).set_sep("\n\n")
