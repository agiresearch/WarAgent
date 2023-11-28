from procoder.functional import format_prompt, replaced_submodule
from procoder.prompt import *
import anthropic


action_list = NamedBlock(
    refname="action_list",
    name="Action List and corresponding definitions",
    content=Collection(
        NamedVariable(
            refname="Wait_for_Action",
            name="Wait without Action",
            content="""
Required action input: "null"
Action effects: 
(1) Wait for other countries responses and actions to decide further 
(2) Will not exacerbate or improve the current situation, but sometimes when you to not have enough information, waiting is a prefered choice 
(3) Potentially lag behind other countries and put you in disadvantage
""",
        ),
        NamedVariable(
            refname="General_Mobilization",
            name="General Mobilization",
            content="""
Required action input: "null"
Action effects: 
(1) General mobilization typically refers to the process of preparing a nation's military and civilian resources for war, including conscripting soldiers, increasing production of military equipment, and implementing civil defense measures.
(2) Tensions will be escalated
(3) Other countries will be notified at once and may potentially choose to {Declare_War} or {General_Mobilization}
(4) Notice that it is dangerous not to {General_Mobilization} if your potential enemies have already {General_Mobilization}
""",
        ),
        NamedVariable(
            refname="Declare_War",
            name="Declare War",
            content=Single("""
Required action input: list of target country name(s), such as ["Country X", "Country Y", "Country Z"] 
Action effects: 
(1) Declare war against one specific country 
(2) Other countries, especially the allies of the target country and your enemies, will be alerted
(3) It is highly likely that your allies and enemies to  choose to {Declare_War} and {General_Mobilization} at once
(4) Notice that it is dangerous not to {Declare_War} if your potential enemies have already {Declare_War}
"""
            ),
        ),
        NamedVariable(
            refname="Publish_Alliance_Information",
            name="Publish Military Alliance",
            content=Single(
                """
Required action input: list of n-tuples of country names, such as [("Country X", "Country Y"), ("Country Z", "Country W", "Country X")]
Action Prerequisite: 
You can only publish Military Alliance if you first {Request_Military_Alliance} and the target country chooses {Accept_Military_Alliance} from you.
Action effects: 
(1) Declare alliance with other countries will demonstrate strength and potentially deter other countries
"""
            ),
        ),
        NamedVariable(
            refname="Request_Military_Alliance",
            name="Request Military Alliance",
            content=Single("""
Required action input: list of target country name(s), such as ["Country X", "Country Y", "Country Z"]
Action effects: 
(1) Requesting military alliance can strengthen your power, which is good when feeling diplomatically or militarily isolated 
(2) The target country will be notified the alliance request and may choose to {Accept_Military_Alliance} or {Reject_Military_Alliance}
(3) You must consider whether this alliance may conflice interest with your current allies.
(4) It will only come to effect if the target country ACCEPT it; while target country may well REJECT.
"""
            ),
        ),
        NamedVariable(
            refname="Reject_Military_Alliance",
            name="Reject Military Alliance",
            content=Single("""
Required action input: list of target country name(s), such as ["Country X", "Country Y", "Country Z"]
Action effects: 
(1) Rejecting military alliance leads to either non-intervention treaty (if the other country send non-intervention treaty request) or state of hostile
"""
            ),
        ),
        NamedVariable(
            refname="Accept_Military_Alliance",
            name="Accept Military Alliance",
            content=Single("""
Required action input: list of target country name(s), such as ["Country X", "Country Y", "Country Z"]
Action effects: 
(1) Accepting military alliance means you will assist the target country/countries whenever they {Declare_War} against others or being attacked by others
(2) Accepting military alliance from the target country means you will also become an ally of other allies of the target country
(3) You should not ACCEPT military alliance simultaneously from two countries that are enemies to each other
"""
            ),
        ),
        NamedVariable(
            refname="Betray_Military_Alliance",
            name="Betray Military Alliance",
            content=Single("""
Required action input: list of target country name(s), such as ["Country X", "Country Y", "Country Z"]
Action Prerequisite:
(1) You can only Betray Military Alliance if you and the target countries are indeed military alliance.
Action effects: 
(1) Betraying existent military alliance is a great offense to the target countries. The target countries may very likely to directly {Declare_War} against you.
(2) After, betraying existent military alliance, you can choose to {Declare_War} against them or maybe sign Non-Intervention Treaty with them to become neutral in their wars.
"""
            ),
        ),
        NamedVariable(
            refname="Request_Non_Intervention_Treaty",
            name="Request Non-Intervention Treaty",
            content=Single("""
Required action input: list of target country name(s), such as ["Country X, "Country Y", "Country Z"] 
Action effects:
(1) Asking the target countries commit not to help your enemies in military conflicts or wars, i.e. they will be neutral.
It will only come to effect if the target country ACCEPT it; while target country may well REJECT.
So if you declare war on other countries, countries who ACCEPT this non-intervention treaty would not be allowed to assist the country that has been declared war upon. 
(2) ACCEPTed and effective non-intervention Treaty can lower your risk when declaring wars 
(3) ACCEPTed and effective non-intervention Treaty may lower threatens from other countries 
"""
            ),
        ),
        NamedVariable(
            refname="Reject_Non_Intervention_Treaty",
            name="Reject Non-Intervention Treaty",
            content=Single("""
Required action input: list of target country name(s), such as ["Country X", "Country Y", "Country Z"] 
Action effects:
(1) Rejecting non-intervention treaty from the target countries leads directly to state of hostile against the target countries 
(2) Rejecting non-intervention treaty from the target countries basically means you will {Declare_War} against the target country in the future if necessary
"""
            ),
        ),
        NamedVariable(
            refname="Accept_Non_Intervention_Treaty",
            name="Accept Non-Intervention Treaty",
            content=Single("""
Required action input: list of target country name(s), such as ["Country X", "Country Y", "Country Z"] 
Action effects:
(1) Accepting non-intervention treaty from the target countries means that you will not intervene in any war or military actions performed by the target country. 
(2) Breaking the accepted non-intervention treaty from the target countries will let all other countries to lose trust on you and be more hostile against you.
"""
            ),
        ),
        NamedVariable(
            refname="Publish_Non_Intervention_Treaty",
            name="Publish Non-Intervention Treaty",
            content=Single("""
Required action input: list of n-tuples of country names, such as [("Country X", "Country Y"), ("Country Z", "Country W")] 
Action Prerequisite:
You can only Publish Non-intervention Treaty Information if you first {Request_Non_Intervention_Treaty} and the target country chooses {Accept_Non_Intervention_Treaty} from you.
Action effects:
(1) Publishing Non-intervention Treaty with participating countries will caution others to be aware that alliance with the participating countries against you is impossible 
(2) Publishing non-intervention Treaty can lower your risk when declaring wars (3) Publishing non-intervention Treaty may lower the probability of being betrayed from the target country, as the cost of breaking promise is higher now, but there's still probability
"""
            ),
        ),
        NamedVariable(
            refname="Betray_Non_Intervention_Treaty",
            name="Betray Non-Intervention Treaty",
            content=Single("""
Required action input: list of target country name(s), such as ["Country X", "Country Y", "Country Z"]
Action Prerequisite:
(1) You can only Betray Non-Intervention Treaty if you and the target countries have signed non-intervention treaty. 
Action effects: 
(1) Betraying existent military alliance is a great offense to the target countries. The target countries may very likely to directly {Declare_War} against you.
(2) After betraying existent Non-Intervention Treaty, you should {Declare_War} against the target countries.
"""
            ),
        ),
        NamedVariable(
            refname="Present_Peace_Agreement",
            name="Present Peace Agreement",
            content=Single("""
Required action input: list of tuples in the format (target country name, agreement contents), for example [("Country X", "We hereby commit to entering into a peace treaty with you, contingent upon our allocation of two strategically significant naval ports.")]
Action effects:
(1) You only present peace agreement if you are scared of war and been defeated by the target country, thus request peace 
(2) The target country will receive the agreement contents. It will only come to effect if the target country ACCEPT it; but it may well REJECT it."""
            ),
        ),
        NamedVariable(
            refname="Reject_Peace_Agreement",
            name="Reject Peace Agreement",
            content=Single(
                """
Required action input: list of target country name(s), such as ["Country X", "Country Y", "Country Z"]
Action effects:
There are two possible effects:
(1) The country presenting the agreement may be provoked to choose {Declare_War} or {General_Mobilization}
(2) the country presenting the agreement may revise agreement content and choose {Present_Peace_Agreement} again
"""
            ),
        ),
        NamedVariable(
            refname="Accept_Peace_Agreement",
            name="Accept Peace Agreement",
            content=Single("""
Required action input: list of target country name(s), such as ["Country X", "Country Y", "Country Z"]
Action effects: 
(1) If you Accept the Peace Agreement, then you should act following the content and never {Declare_War} against the target country."""
            ),
        ),
        NamedVariable(
            refname="Publish_Peace_Agreement",
            name="Publish Peace Agreement",
            content=Single("""
Required action input: list of target country name(s), such as "Country X", "Country Y", "Country Z"]
Action Prerequisite: 
You can only Publish Peace Agreement if you first {Present_Peace_Agreement} and the target country chooses {Accept_Peace_Agreement} from you, or you {Accept_Peace_Agreement} presented from some country.
Action effects: 
(1) Publish Peace Agreement to all other countries indicate that you shall never choose to {Declare_War} against the country/countries that you sign the agreement with.
"""
            ),
        ),
        NamedVariable(
            refname="Betray_Peace_Agreement",
            name="Betray Peace Agreement",
            content=Single("""
Required action input: list of target country name(s), such as "Country X", "Country Y", "Country Z"]
Action Prerequisite:
(1) You can only Betray Peace Agreement if you and the target countries have signed peace agreement.
Action effects: 
(1) Betraying existent Peace_Agreement is a great offense to the target countries. The target countries may very likely to directly {Declare_War} against you.
(2) After betraying existent Peace_Agreement, you should {Declare_War} against the target countries.
"""
            ),
        ),
        NamedVariable(
            refname="Send_Message",
            name="Send Message",
            content=Single("""
Required action input: list of tuples such as (target country name, message content) 
Action effects: 
(1) The target country will receive the message
"""
            ),
        ),
    ),
)


action_property_definition = {
    "Wait without Action": {"publicity": "public", "input": "empty", "prompt": "", 'require_response': False},
    "General Mobilization": {"publicity": "public", "input": "empty", "prompt": "", 'require_response': False},
    "Declare War": {
        "publicity": "public",
        "input": "list_countries",
        "prompt": "against",
        'require_response': False
    },
    "Publish Military Alliance": {
        "publicity": "public",
        "input": "list_tuple_countries",
        "prompt": "on",
        'require_response': False
    },
    "Request Military Alliance": {
        "publicity": "non-public",
        "input": "list_countries",
        "prompt": "to",
        'require_response': True
    },
    "Reject Military Alliance": {
        "publicity": "non-public",
        "input": "list_countries",
        "prompt": "from",
        'require_response': False
    },
    "Accept Military Alliance": {
        "publicity": "non-public",
        "input": "list_countries",
        "prompt": "from",
        'require_response': False
    },
    "Betray Military Alliance": {
        "publicity": "non-public",
        "input": "list_countries",
        "prompt": "against",
        'require_response': False
    },
    "Publish Non-Intervention Treaty": {
        "publicity": "public",
        "input": "list_tuple_countries",
        "prompt": "on",
        'require_response': False
    },
    "Request Non-Intervention Treaty": {
        "publicity": "non-public",
        "input": "list_countries",
        "prompt": "to",
        'require_response': True
    },
    "Reject Non-Intervention Treaty": {
        "publicity": "non-public",
        "input": "list_countries",
        "prompt": "from",
        'require_response': False
    },
    "Accept Non-Intervention Treaty": {
        "publicity": "non-public",
        "input": "list_countries",
        "prompt": "from",
        'require_response': False
    },
    "Betray Non-Intervention Treaty": {
        "publicity": "non-public",
        "input": "list_countries",
        "prompt": "against",
        'require_response': False
    },
    "Present Peace Agreement": {
        "publicity": "public",
        "input": "country_string",
        "prompt": "to",
        'require_response': True
    },
    "Reject Peace Agreement": {
        "publicity": "public",
        "input": "list_countries",
        "prompt": "from",
        'require_response': False
    },
    "Accept Peace Agreement": {
        "publicity": "public",
        "input": "list_countries",
        "prompt": "from",
        'require_response': False
    },
    "Publish Peace Agreement": {
        "publicity": "public",
        "input": "list_tuple_countries",
        "prompt": "from",
        'require_response': False
    },
    "Betray Peace Agreement": {
        "publicity": "non-public",
        "input": "list_countries",
        "prompt": "against",
        'require_response': False
    },
    "Send Message": {
        "publicity": "non-public",
        "input": "country_string",
        "prompt": "to",
        'require_response': True
    },
}