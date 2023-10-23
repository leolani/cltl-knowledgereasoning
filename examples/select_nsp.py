import json
from pathlib import Path

from cltl.brain.long_term_memory import LongTermMemory
from tqdm import tqdm

from cltl.thoughts.thought_selection.nsp_selector import NSP

# Read scenario from file
scenario_file_name = 'thoughts-responses.json'
scenario_json_file = './data/' + scenario_file_name

f = open(scenario_json_file, )
scenario = json.load(f)

# Select thought
selector = NSP('./../src/cltl/reply_generation/thought_selectors/nsp_model')

selected_thoughts = []
for brain_response in tqdm(scenario):
    the_thought = selector.select(brain_response)

    # Save new brain response to file
    brain_response["thoughts"] = the_thought
    selected_thoughts.append(brain_response)

f = open("./data/selections/nsp-selections.json", "w")
json.dump(selected_thoughts, f)
