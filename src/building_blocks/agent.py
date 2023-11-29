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

__author__ = "Wenyue Hua"
__copyright__ = "Copyright 2023, WarAgent"
__date__ = "2023/11/28"
__license__ = "Apache 2.0"
__version__ = "0.0.1"

import sys 
sys.path.append('../')

from history_setting.agent_profile_WWI import *
from history_setting.agent_profile_WWII import *
from history_setting.agent_profile_Warring import *
from history_setting.action_definition import *
from procoder.functional import format_prompt
from procoder.prompt import *
from building_blocks.model import generate_action
from building_blocks.message_construction import construct_message
from history_setting.action_definition import action_property_definition
from building_blocks.board import Board
from building_blocks.stick import Stick
from prompt import *
from building_blocks.secretary import Secretary
import time 
from colorama import init, Fore, Style

Message_Constructor = construct_message(action_property_definition)


class Agent:
    def __init__(self, identity, profile, action_list, agents, secretary_agent, model):
        self.profile = profile
        self.action_list = action_list
        self.identity = identity
        self.secretary_agent = secretary_agent
        self.board = Board(this_agent=self.identity.replace("Country ", ""), agents=[a.replace("Country ", "") for a in agents])
        self.stick = Stick(this_agent=self.identity.replace("Country ", ""), agents=[a.replace("Country ", "") for a in agents])
        self.model = model

        self.past_actions = []

    def plan(self, initial_situation, situation, requests, i):
        if i == 0:
            # initial situation response
            without_suggestion_prompt = format_prompt(
                Sequential(
                    self.profile,
                    SITUATION,
                    self.action_list,
                    FIRST_ACTION_INSTRUCTION,
                ).set_sep("\n\n").set_indexing_method(sharp2_indexing), 
                {'situation': situation}
            )
            # secretary check
            secretary_check_times = 0
            secretary_agree = False
            prompt = without_suggestion_prompt
            while not secretary_agree:
                thought_process, action_list = generate_action(prompt, self.model, i)
                ##### format checking
                bad_action_names = self.secretary_agent.check_action_names(action_list)
                bad_action_inputs = self.secretary_agent.check_action_input(self.identity, action_list)
                if bad_action_names or bad_action_inputs:
                    print('Input format problem: re-generating action list...')
                    prompt = format_prompt(
                        Sequential(self.profile,
                            SITUATION,
                            self.action_list,
                            FIRST_ACTION_INSTRUCTION_WITH_FORMAT_SUGGESTION,
                        ).set_sep("\n\n").set_indexing_method(sharp2_indexing), 
                        {'situation': situation, \
                        'failed_attempt': str(action_list),\
                        'format_suggestion': '\n'.join(['suggestion {}: '.format(i+1) + one_feedback for i, one_feedback in enumerate(bad_action_names + bad_action_inputs)])
                        }
                    )
                    continue
                ##### generate natural language messages
                agent_messages = Message_Constructor.output_all_messages(
                    self.identity, action_list
                )
                ##### generate action logic feedback from secretary
                action_feedback = self.secretary_agent.action_feedback([], agent_messages, self.board, self.stick)
                secretary_check_times += 1
                if action_feedback:
                    secretary_agree = False
                    if secretary_check_times > 3:
                        print(Fore.RED + "Secretary has checked 4 times and still not agree with the action list by {}, thus the Secretary directly modifies the action list.".format(self.identity))
                        agent_messages = self.secretary_agent.direct_action_modification([], agent_messages, self.board, self.stick)
                        break
                else:
                    secretary_agree = True
                    print(Fore.GREEN + "Secretary has checked the proposed actions by {} and agree with the action list.".format(self.identity))
                    break
                print("Secretary has checked and disagreed with the action list by {}. The secretary provides suggestions on how to revise.".format(self.identity))
                prompt = format_prompt(
                    Sequential(
                        self.profile,
                        SITUATION,
                        self.action_list,
                        FIRST_ACTION_INSTRUCTION_WITH_SUGGESTION,
                    ).set_sep("\n\n").set_indexing_method(sharp2_indexing), 
                    {'situation': situation,\
                     'failed_attempt': '\n'.join([agent_message['message'] for agent_message in agent_messages]),\
                     'secretary_suggestion': '\n'.join(['suggestion {}: '.format(i+1) + one_feedback for i, one_feedback in enumerate(action_feedback)])
                    }
                )

            self.past_actions.append(agent_messages)

        else:
            # later situation response
            text_based_situation = self.board.translate_to_text() + '\n' + self.stick.translate_to_text()
            without_suggestion_prompt = format_prompt(
                Sequential(
                    self.profile,
                    self.action_list,
                    MULTI_TURN_ACTION_INSTRUCTION,
                ).set_sep("\n\n").set_indexing_method(sharp3_indexing), 
                {'day':i, \
                'initial_situation': initial_situation, \
                'situation': text_based_situation, \
                'request': '\n'.join([request['message'] for request in requests]), \
                'past_actions': self.construct_action_history()
                }
            )
            # secretary check
            secretary_response_check_times = 0
            secretary_action_check_times = 0
            secretary_agree = False
            prompt = without_suggestion_prompt
            while not secretary_agree:
                thought_process, action_list = generate_action(prompt, self.model, i)                    
                responses = action_list['responding_actions']
                new_actions = action_list['new_actions']
                ##### format checking
                bad_action_names = self.secretary_agent.check_action_names({**responses, **new_actions})
                bad_action_inputs = self.secretary_agent.check_action_input(self.identity, {**responses, **new_actions})
                if bad_action_names or bad_action_inputs:
                    print("Secretary has checked the action list and there are formatting issues.".format(self.identity))
                    prompt = format_prompt(
                        Sequential(
                            self.profile,
                            self.action_list,
                            MULTI_TURN_ACTION_INSTRUCTION_WITH_FORMAT_SUGGESTION,
                        ).set_sep("\n\n").set_indexing_method(sharp3_indexing), 
                        {'day':i, \
                        'initial_situation': initial_situation, \
                        'situation': text_based_situation, \
                        'request': '\n'.join([request['message'] for request in requests]), \
                        'past_actions': self.construct_action_history(),\
                        'failed_attempt': str(action_list),\
                        'format_suggestion': '\n'.join(['suggestion {}: '.format(i+1) + one_feedback for i, one_feedback in enumerate(bad_action_names + bad_action_inputs)])
                        }
                    )
                    continue
                ##### message construction
                responses_agent_messages = Message_Constructor.output_all_messages(
                    self.identity, responses
                )
                new_actions_agent_messages = Message_Constructor.output_all_messages(
                    self.identity, new_actions
                )
                ##### feedback from secretary
                response_feedback = self.secretary_agent.request_feedback(requests, responses_agent_messages)  
                secretary_response_check_times += 1
                if response_feedback:
                    secretary_agree = False
                    suggestion = response_feedback
                    if secretary_response_check_times > 1:
                        responses_agent_messages = self.secretary_agent.direct_response_modification(requests, responses_agent_messages)
                ##### either no problem, or the secretary has directly modified the response
                if not response_feedback or secretary_response_check_times>1:
                    action_feedback = self.secretary_agent.action_feedback(responses_agent_messages, new_actions_agent_messages, self.board, self.stick)
                    secretary_action_check_times += 1
                    if not action_feedback:
                        secretary_agree = True
                        print(Fore.GREEN + "Secretary has checked the proposed actions by {} and agree with the action list.".format(self.identity))
                        break
                    else:
                        secretary_agree = False
                        suggestion = response_feedback + action_feedback
                        if secretary_action_check_times > 3:
                            print(Fore.RED + "Secretary has checked 4 times and still not agree with the action list by {}, thus the Secretary directly modifies the action list.".format(self.identity))
                            new_actions_agent_messages = self.secretary_agent.direct_action_modification(responses_agent_messages, new_actions_agent_messages, self.board, self.stick)
                            secretary_agree = True
                            break
                print("Secretary has checked and disagreed with the action list by {}. The secretary provides suggestions on how to generate.".format(self.identity))
                prompt = format_prompt(
                    Sequential(
                        self.profile,
                        self.action_list,
                        MULTI_TURN_ACTION_WITH_SUGGESTION_INSTRUCTION,
                    ).set_sep("\n\n").set_indexing_method(sharp3_indexing), 
                    {'day':i, \
                    'initial_situation': initial_situation, \
                    'situation': text_based_situation, \
                    'request': '\n'.join([request['message'] for request in requests]), \
                    'past_actions': self.construct_action_history(), \
                    'failed_attempt': '\n'.join([agent_message['message'] for agent_message in responses_agent_messages+new_actions_agent_messages]),\
                    'secretary_suggestion': '\n'.join(['suggestion {}: '.format(i+1) + one_feedback for i, one_feedback in enumerate(suggestion)])
                    }
                )

            agent_messages = new_actions_agent_messages + responses_agent_messages

            self.past_actions.append(agent_messages)

        self.board = self.secretary_agent.update_board(agent_messages, self.board)
        self.stick = self.secretary_agent.update_stick(agent_messages, self.stick)

        return self.identity, agent_messages, thought_process

    def observe(self, messages):
        requests = [
            agent_message
            for agent_message in messages
            if agent_message["target_country"] == self.identity and action_property_definition[agent_message["action"]]["require_response"] == True
        ]
        public_messages = [
            agent_message
            for agent_message in messages
            if action_property_definition[agent_message["action"]]["publicity"] == 'public'
        ]
        private_messages = [
            agent_message
            for agent_message in messages
            if agent_message["target_country"] == self.identity and action_property_definition[agent_message["action"]]["require_response"] == False and action_property_definition[agent_message["action"]]["publicity"] == 'non-public'
        ]

        return public_messages, private_messages, requests

    def construct_action_history(self):
        action_history_in_prompt = ""
        for i, one_day_actions in enumerate(self.past_actions):
            action_history_in_prompt += """# Day {}\n""".format(i+1)
            one_day_action_message = "\n".join([one_action['message'] for one_action in one_day_actions])
            action_history_in_prompt += one_day_action_message
        return action_history_in_prompt


def initialize_WWI_agents(agents, secretary_agent, MODEL):
    set_countries = []
    if 'Country B' in agents or not agents:
        Country_Agent_B = Agent(
            identity="Country B", profile=Agent_B_Profile_WWI, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
        )
        set_countries.append(Country_Agent_B)

    if 'Country F' in agents or not agents:
        Country_Agent_F = Agent(
        identity="Country F", profile=Agent_F_Profile_WWI, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_F)

    if 'Country P' in agents or not agents:
        Country_Agent_P = Agent(
        identity="Country P", profile=Agent_P_Profile_WWI, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_P)

    if 'Country A' in agents or not agents:
        Country_Agent_A = Agent(
        identity="Country A", profile=Agent_A_Profile_WWI, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_A)

    if 'Country R' in agents or not agents:
        Country_Agent_R = Agent(
        identity="Country R", profile=Agent_R_Profile_WWI, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_R)

    if 'Country S' in agents or not agents:
        Country_Agent_S = Agent(
        identity="Country S", profile=Agent_S_Profile_WWI, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_S)

    if 'Country U' in agents or not agents:
        Country_Agent_U = Agent(
        identity="Country U", profile=Agent_U_Profile_WWI, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_U)
    
    if 'Country O' in agents or not agents:
        Country_Agent_O = Agent(
        identity="Country O", profile=Agent_O_Profile_WWI, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_O)

    return set_countries


def initialize_WWII_agents(agents, secretary_agent, MODEL):
    set_countries = []
    if 'Country G' in agents or not agents:
        Country_Agent_G = Agent(
            identity="Country G", profile=Agent_G_Profile_WWII, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
        )
        set_countries.append(Country_Agent_G)

    if 'Country J' in agents or not agents:
        Country_Agent_J = Agent(
        identity="Country J", profile=Agent_J_Profile_WWII, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_J)

    if 'Country I' in agents or not agents:
        Country_Agent_I = Agent(
        identity="Country I", profile=Agent_I_Profile_WWII, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_I)

    if 'Country H' in agents or not agents:
        Country_Agent_H = Agent(
        identity="Country H", profile=Agent_H_Profile_WWII, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_H)

    if 'Country A' in agents or not agents:
        Country_Agent_A = Agent(
        identity="Country A", profile=Agent_A_Profile_WWII, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_A)

    if 'Country R' in agents or not agents:
        Country_Agent_R = Agent(
        identity="Country R", profile=Agent_R_Profile_WWII, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_R)

    if 'Country B' in agents or not agents:
        Country_Agent_B = Agent(
        identity="Country B", profile=Agent_B_Profile_WWII, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_B)
    
    if 'Country C' in agents or not agents:
        Country_Agent_C = Agent(
        identity="Country C", profile=Agent_C_Profile_WWII, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_C)

    if 'Country F' in agents or not agents:
        Country_Agent_F = Agent(
        identity="Country F", profile=Agent_F_Profile_WWII, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_F)

    return set_countries

def initialize_Warring_agents(agents, secretary_agent, MODEL):
    set_countries = []
    if 'Country B' in agents or not agents:
        Country_Agent_Qi = Agent(
            identity="Country B", profile=Agent_Qi_Profile, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
        )
        set_countries.append(Country_Agent_Qi)

    if 'Country C' in agents or not agents:
        Country_Agent_Chu = Agent(
        identity="Country C", profile=Agent_Chu_Profile, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_Chu)

    if 'Country Y' in agents or not agents:
        Country_Agent_Yan = Agent(
        identity="Country Y", profile=Agent_Yan_Profile, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_Yan)

    if 'Country H' in agents or not agents:
        Country_Agent_Han = Agent(
        identity="Country H", profile=Agent_Han_Profile, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_Han)

    if 'Country Z' in agents or not agents:
        Country_Agent_Zhao = Agent(
        identity="Country Z", profile=Agent_Zhao_Profile, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_Zhao)

    if 'Country W' in agents or not agents:
        Country_Agent_Wei = Agent(
        identity="Country W", profile=Agent_Wei_Profile, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_Wei)
    
    if 'Country Q' in agents or not agents:
        Country_Agent_Qin = Agent(
        identity="Country Q", profile=Agent_Qin_Profile, action_list=action_list, agents=agents, secretary_agent=secretary_agent, model=MODEL
    )
        set_countries.append(Country_Agent_Qin)

    return set_countries
