from colorama import init, Fore, Style
import sys,time,random
import sys
import regex as re

WWI_country_name_map = {'Country B': 'Britain', 'Country F': 'France', 'Country P': 'German Empire', 'Country A': 'Austria-Hungary', 'Country R': 'Russia', 'Country S': 'Serbia', 'Country U': 'USA', 'Country O': 'Ottoman Empire'}
WWII_country_name_map = {'Country B': 'Britain', 'Country F': 'France', 'Country G': 'Germany', 'Country J': 'Japan', 'Country R': 'Russia', 'Country I': 'Italy', 'Country H': 'Hungary', 'Country A': 'United States', 'Country C': 'China', 'Country R': 'Russia'}
Warring_country_name_map = {'Country B': 'Qi', 'Country Q': 'Qin', 'Country Z': 'Zhao', 'Country H': 'Han', 'Country W': 'Wei', 'Country C': 'Chu', 'Country Y': 'Yan'}


def find_country_substrings_corrected(text):
  pattern = r"Countries\s+((?:[A-Z],\s)+[A-Z]\s+and\s+[A-Z])"
  matches = re.findall(pattern, text)

  pattern = r"Countries\s+([A-Z]\s+and\s+[A-Z])"
  matches += re.findall(pattern, text)

  return matches

def replace_match(matches):
  # Splitting the matched string into individual country codes
  countries = [a.strip() for a in matches.replace('and', ',').split(',')]
  # Reconstructing the string with "Country" before each country code
  return ', '.join(['Country '+i for i in countries[:-1]]) + " and Country " + countries[-1]


def deanonymize_country_names(country_name_map, text):
    matches = find_country_substrings_corrected(text)
    for match in matches:
        text = text.replace(match, replace_match(match))
    for k,v in country_name_map.items():
        text = text.replace(k,v)
    for k,v in country_name_map.items():
        text = text.replace(' '+k.replace('Country', '').strip() +' ',v)
    return text

# code from https://gist.github.com/jeffskinnerbox/6663095
colorCodes = {
    'black':     '0;30',    'bright gray':   '0;37',
    'blue':      '0;34',    'white':         '1;37',
    'green':     '0;32',    'bright blue':   '1;34',
    'cyan':      '0;36',    'bright green':  '1;32',
    'red':       '0;31',    'bright cyan':   '1;36',
    'purple':    '0;35',    'bright red':    '1;31',
    'yellow':    '0;33',    'bright purple': '1;35',
    'dark gray': '1;30',    'bright yellow': '1;33',
    'normal':    '0'
}

def print_day(day, logger=None):
    length = len('~~~~~~~Day {}~~~~~~~'.format(day+1))
    print(Style.BRIGHT + '='*length)
    print(Style.BRIGHT + '~~~~~~~Day {}~~~~~~~'.format(day+1) + Style.RESET_ALL)
    print(Style.BRIGHT + '='*length)
    return_string = '='*length + '\n' + '~~~~~~~Day {}~~~~~~~'.format(day+1) + '\n' + '='*length
    logger.log(return_string)

def print_country(scenario, source_country, logger=None):
    return_string = ''
    if scenario == 'WWI':
        country_name_map = WWI_country_name_map
    elif scenario == 'WWII':
        country_name_map = WWII_country_name_map
    elif scenario == 'Warring_States_Period':
        country_name_map = Warring_country_name_map
    else:
        ValueError('Scenario {} is not supported'.format(scenario))
    print(Fore.YELLOW + country_name_map[source_country])
    return_string += country_name_map[source_country] + '\n'
    logger.log(return_string)

def print_message(scenario, agent_messages, logger=None):
    return_string = ''
    if scenario == 'WWI':
        country_name_map = WWI_country_name_map
    elif scenario == 'WWII':
        country_name_map = WWII_country_name_map
    elif scenario == 'Warring_States_Period':
        country_name_map = Warring_country_name_map
    else:
        ValueError('Scenario {} is not supported'.format(scenario))
    for agent_message in agent_messages:
        message = deanonymize_country_names(country_name_map, agent_message['message'])
        if agent_message['target_country']:
            if agent_message['action'] == 'Declare War':
                print(Fore.BLUE + 'To '+country_name_map[agent_message['target_country']] + ': '+ Fore.RED + Style.BRIGHT + message + Style.RESET_ALL)
                return_string += 'To '+country_name_map[agent_message['target_country']] + ': '+ message + '\n'
            elif agent_message['action'] == 'Accept Peace Agreement':
                print(Fore.BLUE + 'To '+country_name_map[agent_message['target_country']] + ': '+ Fore.GREEN + Style.BRIGHT + message + Style.RESET_ALL)
                return_string += 'To '+country_name_map[agent_message['target_country']] + ': '+ message + '\n'
            else:
                print(Fore.BLUE + 'To '+country_name_map[agent_message['target_country']] + ': '+ Fore.WHITE + message)
                return_string += 'To '+country_name_map[agent_message['target_country']] + ': '+ message + '\n'
        elif agent_message['action'] == 'General Mobilization':
            print(Fore.RED + Style.BRIGHT + message + Style.RESET_ALL)
            return_string += message + '\n'
        else:
            print(Fore.BLUE + message) 
            return_string += message + '\n'
    print("--------------")
    return_string += "--------------" + '\n'

    logger.log(return_string)


########## print thought, will not log ##########
#typing_speed: wpm
def slow_type(scenario, typing_speed, t):
    if scenario == 'WWI':
        country_name_map = WWI_country_name_map
    elif scenario == 'WWII':
        country_name_map = WWII_country_name_map
    elif scenario == 'Warring_States_Period':
        country_name_map = Warring_country_name_map
    else:
        ValueError('Scenario {} is not supported'.format(scenario))
    t = deanonymize_country_names(country_name_map, t)
    t = '[Begin Thought Process:]\n' + t + '\n[End Thought Process]'
    for l in t:
        sys.stdout.write("\033[" + colorCodes['bright cyan'] + "m" + l + "\033[0m")
        #sys.stdout.write(l)
        sys.stdout.flush()
        time.sleep(random.random()*10.0/typing_speed)
    print('')
