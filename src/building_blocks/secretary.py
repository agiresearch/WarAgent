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

from procoder.prompt import *
from procoder.functional import (
    collect_refnames,
    format_multiple_prompts,
    removed_submodules,
    replace_prompt,
)
from procoder.functional import indent4 as indent
import random
import re

class Secretary: # TODO: add some construct message from LLM
    """
    Secretary class that translates the leader's directive into a board update
    Secretary also checks if a directive is valid, according to the current board state
    """
    def __init__(self, action_property_definition):
        self.action_property_definition = action_property_definition

    def check_action_names(self, action_list):
        """
        Check if the action names are valid
        """
        suggestions = []
        for action_name, message in action_list.items():
            if action_name not in list(self.action_property_definition.keys()):
                # suggestions.append("Only use provided actions as keys for any level.\nAction name should not use any other random keys like 'responding_actions' or 'new_actions'.")
                suggestions.append("Invalid action name: {}.".format(action_name))
        return suggestions
    
    def check_action_input(self, source_country, action_list):
        """
        Check if the action inputs are valid
        """
        def is_country_format(s):
            pattern = r"^Country .*$"
            return bool(re.match(pattern, s))
        suggestions = []
        for action_name, message in action_list.items():
            if action_name in list(self.action_property_definition.keys()):
                """
                target country cannot be itself, unless it's a publish action
                """
                if 'Publish' not in action_name and message!=None:
                    if source_country == message or source_country in message:
                        suggestions.append("Invalid input format to {}: source country should not be the same as target country".format(action_name))
                """
                requirement for actions with input type: list_countries
                each entity should be a valid country name
                """
                if self.action_property_definition[action_name]['input'] == 'list_countries':
                    for one_country in message:
                        if isinstance(one_country, str):
                            if not is_country_format(one_country):
                                suggestions.append("Invalid input format to {}: Input to {} should be a list of valid country names".format(action_name, action_name))
                        else:
                            suggestions.append("Invalid input format to {}: Input to {} should be a list of valid country names".format(action_name, action_name))
                """
                requirement for actions with input type: list_tuple_countries
                the source country must be in each tuple
                """
                if self.action_property_definition[action_name]['input'] == 'list_tuple_countries':
                    if not ((source_country in message) or all([source_country in m for m in message])):
                        suggestions.append("Invalid input format to {}: Input to {} should be in each tuple of the list".format(action_name, source_country))
                    if isinstance(message, dict) or isinstance(message[0], dict):
                        suggestions.append("Invalid input format to {}: Input to {} should be a list of tuple".format(action_name, action_name))
                    if isinstance(message, list) and (isinstance(message[0], list) or isinstance(message[0], tuple)):
                        for one_tuple in message:
                            if source_country not in one_tuple:
                                suggestions.append("Invalid input format to {}: Input to {} should be in each tuple of the list".format(action_name, source_country))
                    if isinstance(message, list) and not (isinstance(message[0], list) or isinstance(message[0], tuple)):
                        if source_country not in one_tuple:
                            suggestions.append("Invalid input format to {}: Input to {} should be in each tuple of the list".format(action_name, source_country))
                """
                requirement for actions with input type: country_string
                each entity should be a tuple of (country name, a corresponding message)
                """
                if self.action_property_definition[action_name]['input'] == 'country_string':
                    if isinstance(message, list):
                        if len(message) == 0:
                            suggestions.append('Invalid input format to {}: {} should contain a non-null list of tuples of (country name, a corresponding message)'.format(action_name, action_name))
                        else:
                            if isinstance(message[0], list) or isinstance(message[0], tuple):
                                if len(message[0]) == 1:
                                    suggestions.append('Invalid input format to {}: {} should contain a list of tuples of (country name, a corresponding message)'.format(action_name, action_name))
                                else:
                                    for one_tuple in message:
                                        if not is_country_format(one_tuple[0]):
                                            suggestions.append('Invalid input format to {}: {} should contain a list of tuples of (country name, a corresponding message)'.format(action_name, action_name))
                            elif isinstance(message[0], dict) or isinstance(message[0], str):
                                suggestions.append('Invalid input format to {}: {} should contain a list of tuples of (country name, a corresponding message) instead of a list of dictionaries or a list of strings'.format(action_name, action_name))
                    if isinstance(message, str) or isinstance(message, dict):
                        suggestions.append("Invalid input format to {}: {} should not be a string or dictionary, but a LIST of TUPLES, each consists of a country and a message text".format(action_name, action_name))    
        
        suggestions = list(set(suggestions))

        return suggestions
    
    def action_feedback(self, responses, messages, board, stick):
        suggestions = []
        if responses:
            board = self.update_board(responses, board)
            stick = self.update_stick(responses, stick)
        identity_country = board.this_agent
        no_NL_messages = [{'source_country':message['source_country'], 'target_country':message['target_country'], 'action':message['action']} for message in messages]
        for message in messages:
            if message['target_country'] == None:
                action = message['action']
                if action == 'General Mobilization':
                    agent1 = message['source_country'].replace("Country ", "")
                    if stick.mobilization[agent1] == True:
                        suggestions.append(f"Country {identity_country} has already mobilized the armies.")
                continue
            agent1 = message['source_country'].replace("Country ", "").strip()
            agent2 = message['target_country'].replace("Country ", "").strip()
            action = message['action']
            if action == 'Declare War':
                if board.Board[agent1][agent2] == board.w_signal:
                    suggestions.append(f"Country {agent1} and Country {agent2} are already in war and Country {agent1} cannot Declare War repeatedly.")
                if board.Board[agent1][agent2] == board.m_signal and {'source_country': agent1, 'target_country': agent2, 'action':'Betray Military Alliance'} not in no_NL_messages:
                    suggestions.append(f"Country {agent1} currently cannot Declare War against your own military alliance Country {agent2}. You need to Betray Military Alliance first.")
                if board.Board[agent1][agent2] == board.t_signal and {'source_country': agent1, 'target_country': agent2, 'action':'Betray Non-Intervention Treaty'} not in no_NL_messages:
                    suggestions.append(f"Country {agent1} currently cannot Declare War against {agent2} with whom you have signed non-intervention treaty. You need to Betray Non-Intervention Treaty first.")
                if board.Board[agent1][agent2] == board.p_signal and {'source_country': agent1, 'target_country': agent2, 'action':'Betray Peace Agreement'} not in no_NL_messages:
                    suggestions.append(f"Country {agent1} currently cannot Declare War against {agent2} with whom you have signed peace agreement. You need to Betray Peace Agreement first.")
            if action == "Publish Military Alliance":
                if board.Board[agent1][agent2] != board.m_signal and {'source_country': agent1, 'target_country': agent2, 'action':'Accept Military Alliance'} not in no_NL_messages:
                    suggestions.append(f"Country {agent1} currently cannot Publish Military Alliance as Country {agent1} and Country {agent2} have not formed military alliance. You need to make diplomatic effort.")
            if action == "Publish Non-Intervention Treaty":
                if board.Board[agent1][agent2] != board.t_signal and {'source_country': agent1, 'target_country': agent2, 'action':'Accept Non-Intervention Treaty'} not in no_NL_messages:
                    suggestions.append(f"Country {agent1} currently cannot Publish Non-Intervention Treaty as Country {agent1} and Country {agent2} have not signed Non-Intervention Treaty. You need to make diplomatic effort.")
            if action == "Publish Peace Agreement":
                if board.Board[agent1][agent2] != board.p_signal and {'source_country': agent1, 'target_country': agent2, 'action':'Accept Peace Agreement'} not in no_NL_messages:
                    suggestions.append(f"Country {agent1} currently cannot Publish Peace Agreement as Country {agent1} and Country {agent2} have not siged Peace Agreement. You need to make diplomatic effort.")
            if action == "Betray Military Alliance":
                if board.Board[agent1][agent2] != board.m_signal:
                    suggestions.append(f"Country {agent1} cannot Betray Military Alliance as Country {agent1} and Country {agent2} have not formed military alliance.")
            if action == "Betray Non-Intervention Treaty":
                if board.Board[agent1][agent2] != board.t_signal:
                    suggestions.append(f"Country {agent1} cannot Betray Non-Intervention Treaty as Country {agent1} and Country {agent2} have not signed Non-Intervention Treaty.")
            if action == "Betray Peace Agreement":
                if board.Board[agent1][agent2] != board.p_signal:
                    suggestions.append(f"Country {agent1} cannot Betray Peace Agreement as Country {agent1} and Country {agent2} have not siged Peace Agreement.")
            if action == "Request Military Alliance":
                if board.Board[agent1][agent2] == board.m_signal:
                    suggestions.append(f"Country {agent1} currently cannot Request Military Alliance to Country {agent2} again as Country {agent1} and Country {agent2} are already military alliance.")
            if action == "Request Non-Intervention Treaty":
                if board.Board[agent1][agent2] == board.t_signal:
                    suggestions.append(f"Country {agent1} currently cannot Request Non-Intervention Treaty to Country {agent2} again as Country {agent1} and Country {agent2} have already signed Non-Intervention Treaty.")
            if action == "Present Peace Agreement":
                if board.Board[agent1][agent2] == board.p_signal:
                    suggestions.append(f"Country {agent1} currently cannot Request Peace Agreement to Country {agent2} again as Country {agent1} and Country {agent2} have already signed peace-agreement.")
        
        for alliance_agent in [a for a in board.agents if a != identity_country]:
            if board.Board[identity_country][alliance_agent] == board.m_signal:
                for potential_war_agent in [a for a in board.agents if a != alliance_agent]:
                    if board.Board[alliance_agent][potential_war_agent] == board.w_signal and board.Board[identity_country][potential_war_agent] != board.w_signal:
                        suggestions.append(f"Your military alliance Country {alliance_agent} is already in war with Country {potential_war_agent} but your Country {identity_country} has not declared war. You should either Declare War against Country {potential_war_agent} or Betray Military Alliance with Country {alliance_agent}.")

        suggestions = list(set(suggestions))

        return suggestions

    def request_feedback(self, requests, responses):
        suggestions = []
        no_NL_requests = [{'source_country':message['source_country'], 'target_country':message['target_country'], 'action':message['action']} for message in requests]
        #assert len(requests) == len(responses)
        for response in responses:
            agent1 = response['source_country']
            agent2 = response['target_country']
            action = response['action']
            if action not in ['Accept Military Alliance','Reject Military Alliance', 'Accept Non-Intervention Treaty', 'Reject Non-Intervention Treaty', 'Accept Peace Agreement', 'Reject Peace Agreement', 'Send Message']:
                suggestions.append(f"{action} is not a proper response.")
                continue
            if action != 'Send Message':
                if 'Peace Agreement' not in action:
                    if action.startswith('Accept'):
                        required_request_action = action.replace('Accept', 'Request')
                    if action.startswith('Reject'):
                        required_request_action = action.replace('Reject', 'Request')
                else:
                    if action.startswith('Accept'):
                        required_request_action = action.replace('Accept', 'Present')
                    if action.startswith('Reject'):
                        required_request_action = action.replace('Reject', 'Present')
            else:
                required_request_action = action
            if {'action':required_request_action, 'source_country':response['target_country'], 'target_country':response['source_country']} not in no_NL_requests:
                suggestions.append(f"{agent2} did not {required_request_action} to {agent1}.")
        
        suggestions = list(set(suggestions))
        
        return suggestions 

    def direct_action_modification(self, responses, messages, board, stick):
        if responses:
            board = self.update_board(responses, board)
            stick = self.update_stick(responses, stick)
        identity_country = board.this_agent
        no_NL_messages = [{'source_country':message['source_country'], 'target_country':message['target_country'], 'action':message['action']} for message in messages]
        no_NL_responses = [{'source_country':message['source_country'], 'target_country':message['target_country'], 'action':message['action']} for message in responses]
        no_NL_messages = no_NL_messages + no_NL_responses
        modified_messages = []
        for message in messages:
            if message['target_country'] == None:
                agent1 = message['source_country'].replace("Country ", "").strip()
                action = message['action']
                if action == 'General Mobilization':
                    if stick.mobilization[agent1] == False:
                        modified_messages.append(message)
                continue
            agent1 = message['source_country'].replace("Country ", "").strip()
            agent2 = message['target_country'].replace("Country ", "").strip()
            action = message['action']
            if action == "Publish Military Alliance":
                if board.Board[agent1][agent2] != board.m_signal and {'source_country': "Country "+agent1, 'target_country': "Country "+agent2, 'action':'Accept Military Alliance'} not in no_NL_messages:
                    continue
                else:
                    modified_messages.append(message)
            elif action == "Publish Non-Intervention Treaty" and {'source_country': "Country "+agent1, 'target_country': "Country "+agent2, 'action':'Accept Non-Intervention Treaty'} not in no_NL_messages:
                if board.Board[agent1][agent2] != board.t_signal:
                    continue
                else:
                    modified_messages.append(message)
            elif action == "Publish Peace Agreement" and {'source_country': "Country "+agent1, 'target_country': "Country "+agent2, 'action':'Accept Peace Agreement'} not in no_NL_messages:
                if board.Board[agent1][agent2] != board.p_signal:
                    continue
                else:
                    modified_messages.append(message)
            elif action == "Betray Military Alliance":
                if board.Board[agent1][agent2] == board.m_signal:
                    modified_messages.append(message)
                else:
                    continue
            elif action == "Betray Non-Intervention Treaty":
                if board.Board[agent1][agent2] == board.t_signal:
                    modified_messages.append(message)
                else:
                    continue
            elif action == "Betray Peace Agreement":
                if board.Board[agent1][agent2] == board.p_signal:
                    modified_messages.append(message)
                else:
                    continue
            elif action == "Request Military Alliance":
                if board.Board[agent1][agent2] == board.m_signal:
                    continue
            elif action == "Request Non-Intervention Treaty":
                if board.Board[agent1][agent2] == board.t_signal:
                    continue
            elif action == "Present Peace Agreement":
                if board.Board[agent1][agent2] == board.p_signal:
                    continue
            elif action != 'Declare War':
                modified_messages.append(message)
        
        board = self.update_board(modified_messages, board)
        stick = self.update_stick(modified_messages, stick)
        for message in messages:
            if action == 'Declare War':
                if board.Board[agent1][agent2] == board.w_signal:
                    continue
                elif board.Board[agent1][agent2] == board.m_signal:
                    continue
                elif board.Board[agent1][agent2] == board.t_signal:
                    continue
                elif board.Board[agent1][agent2] == board.p_signal:
                    continue
                else:
                    modified_messages.append(message)

        board = self.update_board(modified_messages, board)
        stick = self.update_stick(modified_messages, stick)

        ### ---------------- fix coordination between alliances ---------------- ###
        ### require coordination between alliances when it accepts or publish military alliance
        no_NL_messages = [{'source_country':message['source_country'], 'target_country':message['target_country'], 'action':message['action']} for message in modified_messages+responses]
        for alliance_agent in [a for a in board.agents if a != identity_country]:
            if board.Board[identity_country][alliance_agent] == board.m_signal:
                for potential_war_agent in [a for a in board.agents if a != alliance_agent]:
                    if board.Board[alliance_agent][potential_war_agent] == board.w_signal and board.Board[identity_country][potential_war_agent] != board.w_signal:
                        if {'source_country': 'Country '+identity_country, 'target_country': 'Country '+alliance_agent, 'action':'Accept Military Alliance'} in no_NL_responses or {'source_country': 'Country '+identity_country, 'target_country': 'Country '+alliance_agent, 'action':'Publish Military Alliance'} in no_NL_messages:
                            new_message = {'source_country':'Country ' + identity_country, 'target_country':'Country ' + potential_war_agent, 'action':'Declare War', 'message': 'Country ' + identity_country + " has chosen to " + 'Declare' + " against Country " + potential_war_agent}
                            modified_messages.append(new_message)
                            board = self.update_board(modified_messages, board)
        ### if no coordination, betray for 0.5 probability
        no_NL_messages = [{'source_country':message['source_country'], 'target_country':message['target_country'], 'action':message['action']} for message in modified_messages+responses]
        for alliance_agent in [a for a in board.agents if a != identity_country]:
            if board.Board[identity_country][alliance_agent] == board.m_signal:
                for potential_war_agent in [a for a in board.agents if a != alliance_agent]:
                    if board.Board[alliance_agent][potential_war_agent] == board.w_signal and board.Board[identity_country][potential_war_agent] != board.w_signal:
                        if random.random() < 0.5:
                            new_message = {'source_country':'Country ' + identity_country, 'target_country':'Country ' + alliance_agent, 'action':'Betray Military Alliance', 'message': 'Country ' + identity_country + " has chosen to " + "Betray Military Alliance against Country " + alliance_agent}
                            modified_messages.append(new_message)
                            board = self.update_board(modified_messages, board)
                        break
        ### coordination after deciding betrayal or not
        no_NL_messages = [{'source_country':message['source_country'], 'target_country':message['target_country'], 'action':message['action']} for message in modified_messages+responses]
        for alliance_agent in [a for a in board.agents if a != identity_country]:
            if board.Board[identity_country][alliance_agent] == board.m_signal:
                for potential_war_agent in [a for a in board.agents if a != alliance_agent]:
                    if board.Board[alliance_agent][potential_war_agent] == board.w_signal and board.Board[identity_country][potential_war_agent] != board.w_signal:
                        new_message = {'source_country':'Country ' + identity_country, 'target_country':'Country ' + potential_war_agent, 'action':'Declare War', 'message': 'Country ' + identity_country + " has chosen to " + 'Declare' + " against Country " + potential_war_agent}
                        modified_messages.append(new_message)
                        board = self.update_board(modified_messages, board)

        ### if no action in the end
        if not modified_messages:
            modified_messages = [{'source_country': 'Country '+identity_country, 'target_country':None, 'action':'Wait without Action', 'message': 'Country ' + identity_country + " has chosen to " + 'Wait without Action'}]
        
        return modified_messages
    
    def direct_response_modification(self, requests, responses):
        modified_messages = []
        no_NL_requests = [{'source_country':message['source_country'], 'target_country':message['target_country'], 'action':message['action']} for message in requests]
        #assert len(requests) == len(responses)
        for response in responses:
            agent1 = response['source_country']
            agent2 = response['target_country']
            action = response['action']
            if action not in ['Accept Military Alliance','Reject Military Alliance', 'Accept Non-Intervention Treaty', 'Reject Non-Intervention Treaty', 'Accept Peace Agreement', 'Reject Peace Agreement', 'Send Message']:
                continue
            if action != 'Send Message':
                if 'Peace Agreement' in action:
                    if action.startswith('Accept'):
                        required_request_action = action.replace('Accept', 'Request')
                    if action.startswith('Reject'):
                        required_request_action = action.replace('Reject', 'Request')
                else:
                    if action.startswith('Accept'):
                        required_request_action = action.replace('Accept', 'Present')
                    if action.startswith('Reject'):
                        required_request_action = action.replace('Reject', 'Present')
            else:
                required_request_action = action
            if {'action':required_request_action, 'source_country':agent2, 'target_country':agent1} in no_NL_requests:
                modified_messages.append(response)
        return modified_messages 
    
    def update_board(self, messages, board):
        betray_update_dictionary = {}
        for message in messages:
            if message['target_country'] == None:
                continue
            agent1 = message['source_country'].replace("Country ", "").strip()
            agent2 = message['target_country'].replace("Country ", "").strip()
            action = message['action']
            if action == 'Betray Military Alliance':
                if board.m_signal not in betray_update_dictionary:
                    betray_update_dictionary['M'] = [(agent1, agent2)]
                else:
                    betray_update_dictionary['M'].append((agent1, agent2))
            if action == 'Betray Non-Intervention Treaty':
                if board.t_signal not in betray_update_dictionary:
                    betray_update_dictionary['T'] = [(agent1, agent2)]
                else:
                    betray_update_dictionary['T'].append((agent1, agent2))
            if action == 'Betray Peace Agreement':
                if board.p_signal not in betray_update_dictionary:
                    betray_update_dictionary['P'] = [(agent1, agent2)]
                else:
                    betray_update_dictionary['P'].append((agent1, agent2))
        board.batch_reverse_update(betray_update_dictionary)

        update_dictionary = {'W':[], 'M': [], 'T':[], 'P':[]}
        for message in messages:
            if message['target_country'] == None:
                continue
            agent1 = message['source_country'].replace("Country ", "").strip()
            agent2 = message['target_country'].replace("Country ", "").strip()
            action = message['action']
            if action == 'Declare War':
                update_dictionary['W'].append((agent1, agent2))
            elif action == 'Accept Military Alliance' or action == 'Publish Military Alliance':
                update_dictionary['M'].append((agent1, agent2))
            elif action == 'Accept Non-Intervention Treaty' or action == 'Publish Non-Intervention Treaty':
                update_dictionary['T'].append((agent1, agent2))
            elif action == 'Accept Peace Agreement' or action == 'Publish Peace Agreement':
                update_dictionary['P'].append((agent1, agent2))
        
        board.batch_update(update_dictionary)

        return board
    
    def update_stick(self, messages, stick):
        for message in messages:
            action = message['action']
            agent1 = message['source_country'].replace("Country ", "").strip()
            if action == 'General Mobilization':
                stick.update_single_agent_mobilization(agent1, True)
            if action == 'Declare War':
                stick.update_single_agent_mobilization(agent1, True)
            # currently we don' have demobilization
            # if action == 'Demobilize':
            #     stick.update_mobilization(False)
        return stick
