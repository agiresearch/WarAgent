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

import re
import sys 
sys.path.append('../')

from utils import *

from building_blocks.model import *

class construct_message:
    def __init__(self, action_property_definition):
        self.actions = list(action_property_definition.keys())
        self.action_property_definition = action_property_definition

    """Input to each type of message constructor:

    Args:
        source country
        [message]:
        type: could be a single string [Country X],
        or a list of strings [Country X, Country Y],
        or [Country X, content]

    Returns:
        str

    Raises:
        ValueError: If the action does not exist or the input format is wrong
    """

    def empty_input_message(self, source, message):
        # no specific target country
        action = message[0]
        message = source + " has chosen to " + action
        return None, message

    def list_countries_message(self, source, message, prompt):
        action = message[0]
        if isinstance(message[1], list) or isinstance(message[1], tuple):
            country = message[1][0]
        else:
            assert isinstance(message[1], str)
            country = message[1]
        message = source + " has chosen to " + action + " " + prompt + " " + country

        target_country = country
        return target_country, message

    def list_tuples_countries_message(self, source, message, prompt):
        action = message[0]
        if source not in message[1]:
            assert source.replace('Country ', '') in message[1]
            message[1] = ['Country '+ c for c in message[1]]
        countries = " and ".join(message[1])
        
        target_country = [c for c in message[1] if c != source][0]

        message = source + " has chosen to " + action + " " + prompt + " " + countries

        return target_country, message

    def list_country_string_message(self, source, message, prompt):
        # get action
        action = message[0]

        if isinstance(message[1], list) or isinstance(message[1], tuple):
            country = message[1][0]
            content = message[1][1]
        else:
            assert isinstance(message[1], dict)
            country = list(message[1].keys())[0]
            content = list(message[1].values())[0]
        
        # final construct the message
        message = (
            source
            + " has chosen to "
            + action
            + " "
            + prompt
            + " "
            + country
            + " with the following content: "
            + content
        )
        target_country = country
        return target_country, message

    def construct_one_message_from_scratch(self, source_country, message):
        action = message[0]
        input_type = self.action_property_definition[action]["input"]
        prompt = self.action_property_definition[action]["prompt"]
        if input_type == "empty":
            target_country, message = self.empty_input_message(source_country, message)
        elif input_type == "list_countries":
            target_country, message = self.list_countries_message(
                source_country, message, prompt
            )
        elif input_type == "list_tuple_countries":
            tuple_list = message[1]
            if (isinstance(tuple_list[0], tuple) or isinstance(tuple_list[0], list)):
                target_country = []
                constructed_message = []
                for each_tuple in tuple_list:
                    splitted_message = [message[0], each_tuple]
                    one_target_country, one_message = self.list_tuples_countries_message(
                        source_country, splitted_message, prompt
                    )
                    target_country.append(one_target_country)
                    constructed_message.append(one_message)
                message = constructed_message
            else:
                target_country, message = self.list_tuples_countries_message(
                    source_country, message, prompt
                )
        elif input_type == "country_string":
            target_country, message = self.list_country_string_message(
                source_country, message, prompt
            )
        else:
            raise ValueError("Invalid JSON string: cannot find action input type ")

        return target_country, message

    def output_all_messages(self, source_country, country_actions):
        final_messages = []
        for action, messages in country_actions.items():
            if messages is None:
                target_country, message = self.construct_one_message_from_scratch(
                    source_country, [action]
                )
                final_messages.append(
                    {
                        "source_country": source_country,
                        "target_country": target_country,
                        "message": message,
                        'action':action
                    }
                )
            elif isinstance(messages, int) or isinstance(messages, str):
                if isinstance(messages, int):
                    messages = str(messages)
                target_country, message = self.construct_one_message_from_scratch(
                    source_country, [action, messages]
                )
                final_messages.append(
                    {
                        "source_country": source_country,
                        "target_country": target_country,
                        "message": message,
                        'action':action
                    }
                )
            else:
                for message in messages:
                    target_country, message = self.construct_one_message_from_scratch(
                        source_country, [action] + [message]
                    )
                    if isinstance(message, list):
                        for one_target_country, one_message in zip(target_country,message):
                            final_messages.append(
                                {
                                "source_country": source_country,
                                "target_country": one_target_country,
                                "message": one_message,
                                'action':action
                                }
                            )
                    else:
                        final_messages.append(
                        {
                            "source_country": source_country,
                            "target_country": target_country,
                            "message": message,
                            'action':action
                        }
                        )
        return final_messages
