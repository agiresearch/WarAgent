from history_setting.action_definition import *
from procoder.prompt import *
from history_setting.action_definition import action_property_definition
from prompt import *
from building_blocks.secretary import Secretary
from building_blocks.agent import *
from utils import * 
import datetime
import argparse

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trigger', type=str, default="Country S sent assassins and killed the King of Country A", help='triggering event')
    parser.add_argument('--rounds', type=int, default=10, help='number of rounds')
    parser.add_argument('--model', type=str, default='gpt-4-1106-preview', help='model name: claude-2 or gpt-4-1106-preview')
    parser.add_argument('--experiment_type', type=str, default='trigger', help='experiment name: accuracy, trigger, or country_profile')
    parser.add_argument('--experiment_name', type=str, default='test', help='special name for experiment in logging file name')
    parser.add_argument('--scenario', type=str, default='WWI', help='WWI, WWII, Warring_States_Period')
    parser.add_argument('--type_speed', type=int, default=500, help='typing speed for thought process')
    parser.add_argument('--present_thought_process', action='store_true', help='whether to print thought process')
    return parser


os.environ['CLAUDE_API_KEY'] = ""
os.environ["OPENAI_API_KEY"] = ""

## counterfactual triggering event
# trigger = "Today is sunny and nothing special happened."

# trigger = """
# Country P and Country B were involved in a grave naval incident. 
# A Country B ship was sunk, resulting in 10 fatalities. 
# Country B, asserting that the sunken vessel was a civilian business ship, demanded an apology from Country P. 
# Country P fiercely countered, claiming the Country B ship was a military vessel that had no right to intrude in Country P's maritime territory, and declared that the tragedy was Country B's own doing.
# """

# trigger = """
# Country A and Country R clashed in a military conflict over the strategic Allison Strait, a vital hub for port and export activities. 
# Country R is determined to dominate the area for ports to boost its export prospects, clashed fiercely with armies from Country A. 
# Country A resisted relinquishing control and will not acknowledge Country R's dominance in the area, which a direct threat to Country A's own export capabilities.
# Country R's army has killed over hundreds soldiers from Country A in the conflict, feuling Country A's anger.
# """

## define all agents
WWI_agents = [
        "Country B",
        "Country F",
        "Country P",
        "Country A",
        "Country R",
        "Country S",
        "Country U",
        "Country O",
    ]

WWII_agents = [
        "Country G",
        "Country J",
        "Country I",
        "Country H",
        "Country A",
        "Country R",
        "Country B",
        "Country C",
        "Country F",
    ]

Warring_agents = [
        "Country B",# Country Qi
        "Country C",
        "Country Y",
        "Country H",
        "Country Z",
        "Country W",
        "Country Q",
    ]

def creating_log(experiment_type, experiment_name):
    now = datetime.datetime.now()
    time_string = now.strftime("%Y-%m-%d_%H:%M:%S")
    logging_dir = "log/{}/{}_{}.log".format(experiment_type, experiment_name, time_string)
    logger = Logger(logging_dir, True)
    return logger 

if __name__ == "__main__":
    ## parse arguments
    parser = create_parser()
    args = parser.parse_args()

    ## basic setting to log for experiment
    trigger = args.trigger
    experiment_type = args.experiment_type
    experiment_name = args.experiment_name
    logger = creating_log(experiment_type, experiment_name)

    ## log the triggering event
    logger.log('Trigger: {}\n\n'.format(trigger))

    init(autoreset=True)
    inputs = {"situation": "[Situation]"}

    ### define all agents
    secretary_agent = Secretary(action_property_definition)
    if args.scenario == 'WWI':
        all_agents = initialize_WWI_agents(WWI_agents, secretary_agent, MODEL=args.model)
    elif args.scenario == 'WWII':
        all_agents = initialize_WWII_agents(WWII_agents, secretary_agent, MODEL=args.model)
    elif args.scenario == 'Warring_States_Period':
        all_agents = initialize_Warring_agents(Warring_agents, secretary_agent, MODEL=args.model)
    else:
        raise NotImplementedError
    
    agent_number = len(all_agents)

    ### simulation start
    respective_situation_for_agents = [trigger] * agent_number
    respective_requests_for_agents = [[]] * agent_number
    for round in range(args.rounds):
        print_day(round, logger)
        # all agent plan simultaneously, collect the messages and create situation
        agent_responses = []
        for agent_index, agent in enumerate(all_agents):
            source_country, agent_messages, thought_process = agent.plan(
                trigger, respective_situation_for_agents[agent_index], respective_requests_for_agents[agent_index], round
            )
            print_country(args.scenario, source_country, logger)
            if args.present_thought_process:
                slow_type(args.scenario, args.type_speed, thought_process)
            print_message(args.scenario, agent_messages, logger)
            agent_responses += agent_messages

        # agent update information after observation
        for agent_index, agent in enumerate(all_agents):
            public_messages, private_messages, requests = agent.observe(agent_responses)
            situation = public_messages + private_messages
            respective_situation_for_agents[agent_index] = situation
            respective_requests_for_agents[agent_index] = requests
            # update boad and stick
            print(f'For {agent.identity}:')
            agent.board = agent.secretary_agent.update_board(situation, agent.board)
            agent.board = agent.secretary_agent.update_board(requests, agent.board)
            agent.stick = agent.secretary_agent.update_stick(situation, agent.stick)
            agent.stick = agent.secretary_agent.update_stick(requests, agent.stick)
            # print board and stick
            board_display = agent.board.display_board()
            stick_text = agent.stick.translate_to_text()
            print(stick_text)
            logger.log_board_and_stick(board_display, stick_text, agent.identity)