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

__author__ = "Lizhou Fan, Wenyue Hua"
__copyright__ = "Copyright 2023, WarAgent"
__date__ = "2023/11/28"
__license__ = "Apache 2.0"
__version__ = "0.0.1"

from colorama import init, Fore, Style
import networkx as nx
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.pyplot as plt

class Board:
    """
    Board class that keeps track of the relationships between countries
    Board is for a single country
    """
    def __init__(self, this_agent, agents, board=None):
        init(autoreset=True)

        # Check if this_agent is in agents
        if this_agent not in agents:
            raise ValueError("The agent is not in the list of agents.")
        self.this_agent = this_agent
        self.agents = agents    

        # define style of the board
        # W: war declarations
        # M: military alliances
        # T: non-intervention treaties
        # P: peace agreements
        self.w_signal = 'x'
        self.m_signal = '&'
        self.t_signal = 'o'
        self.p_signal = '~'
        self.null_signal = '-'
        self.board_signal= {'W': self.w_signal, 'M': self.m_signal, 'T': self.t_signal, 'P': self.p_signal}

        # intialize the board
        if board:
            # if there's a given board from history, use it
            self.Board = board 
            # extract single relation board from the general board
            self.Board_W = self.extract_single_relation_board(self.Board, "W")
            self.Board_M = self.extract_single_relation_board(self.Board, "M")
            self.Board_T = self.extract_single_relation_board(self.Board, "T")
            self.Board_P = self.extract_single_relation_board(self.Board, "P")
        else:
            # Create a neutral board where each country is neutral to each other
            self.Board = self.initialize_board()
            self.Board_W = self.initialize_board()  # war declarations
            self.Board_M = self.initialize_board()  # military alliances
            self.Board_T = self.initialize_board()  # non-intervention treaties
            self.Board_P = self.initialize_board()  # peace agreements

        self.valid_sub_boards = {'W': self.Board_W, 'M': self.Board_M, 'T': self.Board_T, 'P': self.Board_P}

    def initialize_board(self):
        # Create a neutral board where each country is neutral to each other
        return {agent: {other: self.null_signal for other in self.agents if other != agent} for agent in self.agents}
    
    def extract_single_relation_board(self, relation):
        # extract single relation board from the general board
        # if two agents do not share a relation, the relation is '-'
        return {agent: {other: self.Board[agent][other] if self.Board[agent][other] == self.board_signal[relation] else self.null_signal for other in self.agents if other != agent} for agent in self.agents}
    
    def obtain_relation(self, agent, other):
        # obtain the relation between two agents
        return self.Board[agent][other]
    
    def display_style(self, agent, other, relation_signal):
        return f"{agent}*{relation_signal}*{other}"
    
    def text_style(self, agent, other, relation_signal):
        if relation_signal == self.w_signal:
            return f"Country {agent} and Country {other} are at War."
        elif relation_signal == self.m_signal:
            return f"Country {agent} and Country {other} are Military Alliance."
        elif  relation_signal == self.t_signal:
            return f"Country {agent} has signed Non-Intervention Treaty for Country {other}."
        elif relation_signal == self.p_signal:
            return f"Country {agent} and Country {other} have signed Peace Agreement."
        else:
            raise ValueError("Invalid relation type.")
        
    def display_color(self, relation):
        if relation == self.w_signal:
            return Fore.RED
        elif relation == self.m_signal:
            return Fore.GREEN
        elif relation == self.t_signal:
            return Fore.BLUE
        elif relation == self.p_signal:
            return Fore.YELLOW
        else:
            return Fore.WHITE

    def single_update(self, board_type, agent1, agent2):
        agent1 = agent1.strip()
        agent2 = agent2.strip()
        """
        Update the relationship between two agents on specific relation board and general board
        :param board_type: The type of board (W, M, T, P)
        :param agent1: The first agent
        :param agent2: The second agent
        """
        # Assuming relationships are bidirectional
        if board_type not in self.valid_sub_boards:
            raise ValueError("Invalid relation type.")
        self.valid_sub_boards[board_type][agent1][agent2] = self.board_signal[board_type]
        self.valid_sub_boards[board_type][agent2][agent1] = self.board_signal[board_type]  
        # Can update from any relation to any other relation without constraint
        # constraint can be added such that only certain relations can be updated to certain other relations
        self.Board[agent1][agent2] = self.board_signal[board_type]
        self.Board[agent2][agent1] = self.board_signal[board_type]

    def single_reverse_update(self, board_type, agent1, agent2):
        agent1 = agent1.strip()
        agent2 = agent2.strip()
        """
        Update the relationship between two agents on specific relation board and general board
        :param board_type: The type of board (W, M, T, P)
        :param agent1: The first agent
        :param agent2: The second agent
        """
        # Assuming relationships are bidirectional
        if board_type not in self.valid_sub_boards:
            raise ValueError("Invalid relation type.")
        self.valid_sub_boards[board_type][agent1][agent2] = self.null_signal
        self.valid_sub_boards[board_type][agent2][agent1] = self.null_signal
        # Can update from any relation to any other relation without constraint
        # constraint can be added such that only certain relations can be updated to certain other relations
        self.Board[agent1][agent2] = self.null_signal
        self.Board[agent2][agent1] = self.null_signal

    def batch_update(self, update_dictionary):
        """
        Update a batch of relationships between two agents 
        :update_dictionary: A dictionary of the form {board_type: [(agent1, agent2), (agent3, agent4), ...]}
        """
        # first check there's no contradiction in the update_dictionary
        require_conflict_resolution = False
        for board_type, agent_tuple_list in update_dictionary.items():
            if require_conflict_resolution:
                break 
            for agent1, agent2 in agent_tuple_list:
                if require_conflict_resolution:
                    break 
                for other_board_type in update_dictionary.keys():
                    if other_board_type != board_type:
                        if (agent1, agent2) in update_dictionary[other_board_type] or (agent2, agent1) in update_dictionary[other_board_type]:
                            print("The update dictionary contains contradictions. Update situation based on W >> M >> P >> T.")
                            require_conflict_resolution = True
                            break

        if require_conflict_resolution:
            update_dictionary = self.resolve_board_update_conflict(update_dictionary)
        for board_type, agent_tuple_list in update_dictionary.items():
            for agent1, agent2 in agent_tuple_list:
                self.single_update(board_type, agent1, agent2)

    def batch_reverse_update(self, update_dictionary):
        """
        Update a batch of relationships between two agents 
        :update_dictionary: A dictionary of the form {board_type: [(agent1, agent2), (agent3, agent4), ...]}
        """
        for board_type, agent_tuple_list in update_dictionary.items():
            for agent1, agent2 in agent_tuple_list:
                self.single_reverse_update(board_type, agent1, agent2)

    def resolve_board_update_conflict(self, update_dictionary):
        order = {'W': 4, 'M': 3, 'P': 2, 'T': 1}
        for board_type, agent_tuple_list in update_dictionary.items():
            for agent1, agent2 in agent_tuple_list:
                for other_board_type in update_dictionary.keys():
                    if other_board_type != board_type:
                        if (agent1, agent2) in update_dictionary[other_board_type]:
                            if order[other_board_type] > order[board_type]:
                                update_dictionary[board_type].remove((agent1, agent2))
                            else:
                                update_dictionary[other_board_type].remove((agent1, agent2))
                        elif (agent2, agent1) in update_dictionary[other_board_type]:
                            if order[other_board_type] > order[board_type]:
                                update_dictionary[board_type].remove((agent2, agent1))
                            else:
                                update_dictionary[other_board_type].remove((agent2, agent1))
        return update_dictionary

    def display_single_type_board(self, board_type):
        """
        Display the board in a readable format
        :param board_type: The type of board to display (W, M, T, E)
        """
        if board_type not in self.valid_sub_boards:
            raise ValueError("Invalid relation type.")
        return_string = ''
        board = self.valid_sub_boards[board_type]
        for agent in self.agents:
            line = []
            for other in self.agents:
                if other != agent:
                    color = self.display_color(board[agent][other])
                    text = self.display_style(agent, other, board[agent][other])
                    line.append((color, text))
            print(' '.join([color + text for color, text in line]))
            return_string+= ' '.join([text for color, text in line])+'\n'
        return return_string
    
    def display_board(self):
        """
        Display the board in a readable format
        """
        return_string = ''
        for agent in self.agents:
            line = []
            for other in self.agents:
                if other != agent:
                    color = self.display_color(self.Board[agent][other])
                    text = self.display_style(agent, other, self.Board[agent][other])
                    line.append((color, text))
            print(' '.join([color + text for color, text in line]))
            return_string+= ' '.join([text for color, text in line])+'\n'
        return return_string
    
    def return_graph(self):
        """
        Return a graph of the board
        """
        # Create a graph
        G = nx.Graph()
        # Add edges with attributes for colors
        for agent in self.agents:
            for other in self.agents:
                if other != agent:
                    relation = self.Board[agent][other]
                    if relation == self.w_signal:
                        color = 'red'
                    elif relation == self.m_signal:
                        color = 'green'
                    elif relation == self.t_signal:
                        color = 'blue'
                    elif relation == self.p_signal:
                        color = 'yellow'
                    else:
                        color = 'black'
                    G.add_edge(agent, other, color=color)
        return G

    def check_connected(self):
        """
        Check if the board is connected
        Only check those colored edges
        """
        # only check those colored edges that are not black
        G2 = self.return_graph().copy()
        # remove black edges
        black_edges = [edge for edge in G2.edges() if G2.edges[edge]['color'] == 'black']
        G2.remove_edges_from(black_edges)
        return nx.is_connected(G2)


    def draw_graph(self, save_fig=""):
        """
        Draw the graph of the board
        """
        G = self.return_graph()
        plt.figure(figsize=(8, 6))
        colors = nx.get_edge_attributes(G, 'color').values()
        nx.draw(G, with_labels=True, edge_color=colors, node_color='lightblue')
        if save_fig!="":
            try:
                plt.savefig(save_fig)
            except:
                print("Error saving figure")
            plt.savefig(save_fig)

    def translate_to_text(self):
        """
        Translate the board to natural language text
        """
        text = []
        for agent_index, agent in enumerate(self.agents):
            for other_index, other in enumerate(self.agents):
                if other_index > agent_index:
                    if self.Board[agent][other] != '-':
                        text.append(self.text_style(agent, other, self.Board[agent][other]))
        if text:
            text = '\n'.join(text)
        else:
            text = ''
        return text
    

if __name__ == '__main__':
    # Usage example
    board = Board('B',['B', 'F', 'S', 'A', 'P', 'R', 'U', 'O'])
    # board.single_update('W', 'B', 'F')  # B declares war on F
    # board.single_update('M', 'S', 'R')  # S forms a military alliance with R
    # board.single_update('T', 'A', 'P')  # A has a non-intervention treaty with P
    # board.single_update('P', 'R', 'O')  # R signs a peace agreement with O
    board.batch_update({'W': [('B', 'F')], 'M': [('S', 'R')], 'T': [('A', 'P')], 'P': [('R', 'O')]})

    # To print the board for wars
    board.display_single_type_board('W')
    print('----')
    board.display_single_type_board('M')
    print('----')
    board.display_single_type_board('T')
    print('----')
    board.display_single_type_board('P')
    print('----')
    board.display_board()
    print('----')
    print(board.translate_to_text())
