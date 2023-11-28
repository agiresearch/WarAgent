class Stick:
    """
    Stick class that keeps track of the internal record of a single country
    Stick is for a single country:
        MO (mobilization): binary (True for mobilized, False for not mobilized)
        IN (internal stability): 'low', 'medium', 'high'
        WR (war readiness prediction): 'low', 'medium', 'high'
    """
    def __init__(self, this_agent, agents, stick=None):
        self.this_agent = this_agent
        self.agents = agents
        assert self.this_agent in self.agents

        # intialize the stick
        if stick:
            # if there's a given stick from history, use it
            self.get_set_values(stick)
        else:
            # Create a neutral stick where each country is neutral to each other
            self.initialize_stick()

    def initialize_stick(self):
        # Create a neutral board where each country is neutral to each other
        self.mobilization = {agent: False for agent in self.agents}
    
        # self.stability = stability
        # self.war_readiness = war_readiness

    def get_set_values(self, stick):
        self.mobilization = stick.mobilization
        # self.stability = stick['Internal Stability']
        # self.war_readiness = stick['War Readiness']

    def update_single_agent_mobilization(self, agent, status):
        self.mobilization[agent] = status
        # self.stability = stability
        # self.war_readiness = war_readiness

    # def update_stability(self, level):
    #     if level in ['low', 'medium', 'high']:
    #         self.stability = level
    #     else:
    #         raise ValueError("Invalid stability level.")

    # def update_war_readiness(self, level):
    #     if level in ['low', 'medium', 'high']:
    #         self.war_readiness = level
    #     else:
    #         raise ValueError("Invalid war readiness level.")

    def get_status(self, agent):
        return self.mobilization[agent]
    
    def translate_to_text(self):
        stick_text = ""
        # mobilization
        for agent, mobilized in self.mobilization.items():
            if mobilized:
                stick_text += "Country {}'s army is mobilized. ".format(agent)
        return stick_text

    def __str__(self):
        return self.translate_to_text()

if __name__ == '__main__':
    # Initialize the Stick class for a country
    stick = Stick('A')
    print(stick)

    # Example updates
    stick.update_mobilization(True)  # A has mobilized

    # Output the status as a string
    print(stick)