import copy
import json

from tqdm import tqdm

from cltl.thoughts.thought_selection.pertype_selector import PerTypeSelector

# Read scenario from file
scenario_file_name = 'thoughts-responses.json'
scenario_json_file = './data/brain_responses/' + scenario_file_name

f = open(scenario_json_file, )
scenario = json.load(f)

# Initialize
thought_types = ['_complement_conflict', '_negation_conflicts',
                 '_statement_novelty', '_entity_novelty',
                 '_subject_gaps', '_complement_gaps',
                 '_overlaps', '_trust']
selectors = []
for thought_type in thought_types:
    selector = PerTypeSelector(thought_type)
    selectors.append(selector)

# Select thought
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

    for selector in selectors:
        this_brain_response = copy.deepcopy(brain_response)
        this_brain_response["thoughts"] = selector.select(this_brain_response)
        print(f"\tChosen thought: {list(this_brain_response['thoughts'].keys())[0]}")

        # Save new brain response to file
        selected_thoughts.append(this_brain_response)

f = open("./data/selections/pertype-selections.json", "w")
json.dump(selected_thoughts, f)
