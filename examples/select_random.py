import json

from tqdm import tqdm

from cltl.thoughts.thought_selection.random_selector import RandomSelector

# Read scenario from file
scenario_file_name = 'thoughts-responses.json'
scenario_json_file = './data/brain_responses/' + scenario_file_name

f = open(scenario_json_file, )
scenario = json.load(f)

# Select thought
selector = RandomSelector()

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
    brain_response["thoughts"] = selector.select(brain_response)
    print(f"\tChosen thought: {list(brain_response['thoughts'].keys())[0]}")

    # Save new brain response to file
    selected_thoughts.append(brain_response)

f = open("./data/selections/random-selections.json", "w")
json.dump(selected_thoughts, f)
