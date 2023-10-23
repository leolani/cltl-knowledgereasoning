import json
from pathlib import Path

from cltl.brain.long_term_memory import LongTermMemory
from tqdm import tqdm

from cltl.thoughts.thought_selection.rl_selector import UCB

# Read scenario from file
scenario_file_name = 'thoughts-responses.json'
scenario_json_file = './data/' + scenario_file_name

f = open(scenario_json_file, )
scenario = json.load(f)

# Select thought
brain = LongTermMemory(address="http://localhost:7200/repositories/sandbox",
                       log_dir=Path("./data/brain_logs/"),
                       clear_all=False)
selector = UCB(brain, savefile='./../src/cltl/thoughts/thought_selection/rl_model/thoughts.json')

selected_thoughts = []
for brain_response in tqdm(scenario):
    selector.reward_thought()
    the_thought = selector.select(brain_response)

    # Save new brain response to file
    brain_response["thoughts"] = the_thought
    selected_thoughts.append(brain_response)

f = open("./data/selections/rl-selections.json", "w")
json.dump(selected_thoughts, f)
