import json
from pathlib import Path

from cltl.brain.long_term_memory import LongTermMemory
from tqdm import tqdm

from cltl.thoughts.thought_selection.rl_selector import UCB

# Read scenario from file
scenario_file_name = 'thoughts-responses.json'
scenario_json_file = './data/brain_responses/' + scenario_file_name

f = open(scenario_json_file, )
scenario = json.load(f)

# Select thought
brain = LongTermMemory(address="http://localhost:7200/repositories/sandbox",
                       log_dir=Path("./data/brain_logs/"),
                       clear_all=False)
selector = UCB(brain, savefile='./../src/cltl/thoughts/thought_selection/rl_model/thoughts.json')

selected_thoughts = []
for brain_response in tqdm(scenario):
    print(f"\nTriple: {brain_response['statement']['subject']['label']} "
          f"{brain_response['statement']['predicate']['label']} "
          f"{brain_response['statement']['object']['label']} "
          f"by {brain_response['statement']['author']['label']}, "
          f"\tcertainty: {brain_response['statement']['perspective']['_certainty']} "
          f"polarity: {brain_response['statement']['perspective']['_polarity']} "
          f"sentiment: {brain_response['statement']['perspective']['_sentiment']} "
          f"emotion: {brain_response['statement']['perspective']['_emotion']}")

    selector.reward_thought()
    brain_response["thoughts"] = selector.select(brain_response)
    print(f"\tChosen thought: {list(brain_response['thoughts'].keys())[0]}")

    # Save new brain response to file
    selected_thoughts.append(brain_response)

f = open("./data/selections/rl-selections.json", "w")
json.dump(selected_thoughts, f)
