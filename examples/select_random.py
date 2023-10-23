import json

from tqdm import tqdm

from cltl.thoughts.thought_selection.random_selector import RandomSelector

# Read scenario from file
scenario_file_name = 'thoughts-responses.json'
scenario_json_file = './data/' + scenario_file_name

f = open(scenario_json_file, )
scenario = json.load(f)

# Select thought
selector = RandomSelector()

selected_thoughts = []
for brain_response in tqdm(scenario):
    the_thought = selector.select(brain_response)

    # Save new brain response to file
    brain_response["thoughts"] = the_thought
    selected_thoughts.append(brain_response)

f = open("./data/selections/random-selections.json", "w")
json.dump(selected_thoughts, f)
