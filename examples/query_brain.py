"""
THIS SCRIPT SHOWS HOW TO QUERY A KNOWLEDGE GRAPH HOSTED IN GRAPHDB USING THE cltl.brain PACKAGE FROM
https://github.com/leolani/cltl-knowledgerepresentation

It first populates the brain with a handful of "be-from" facts, then asks it a few questions about
those facts (who is from where, where is X from, does X know Y), printing and saving the responses.

Requirements:
- A running GraphDB Free instance with a repository called "sandbox"
  (see http://graphdb.ontotext.com/ and the cltl-knowledgerepresentation README for setup instructions)
- The cltl.brain package installed (a dependency of this project, from cltl-knowledgerepresentation)
"""

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from random import getrandbits
from tempfile import TemporaryDirectory

from cltl.brain.long_term_memory import LongTermMemory
from cltl.brain.utils.helper_functions import brain_response_to_json
from cltl.commons.discrete import UtteranceType

context_id = getrandbits(8)
place_id = getrandbits(8)
start_date = date.today()

context_capsule = {
    "context_id": context_id,
    "date": start_date,
    "place": "Piek's office",
    "place_id": place_id,
    "country": "Netherlands",
    "region": "North Holland",
    "city": "Amsterdam",
}

statement_capsules = [
    {
        "chat": 1,
        "turn": 1,
        "author": {"label": "piek", "type": ["person"], "uri": "http://cltl.nl/leolani/friends/piek-1"},
        "utterance": "Lenka is from Serbia",
        "utterance_type": UtteranceType.STATEMENT,
        "position": "0-25",
        "subject": {"label": "lenka", "type": ["person"], "uri": "http://cltl.nl/leolani/world/lenka-1"},
        "predicate": {"label": "be-from", "uri": "http://cltl.nl/leolani/n2mu/be-from"},
        "object": {"label": "serbia", "type": ["location"], "uri": "http://cltl.nl/leolani/world/serbia"},
        "perspective": {"certainty": 1, "polarity": 1, "sentiment": 0},
        "timestamp": datetime.combine(start_date, datetime.now().time()),
        "context_id": context_id,
    },
    {
        "chat": 1,
        "turn": 2,
        "author": {"label": "piek", "type": ["person"], "uri": "http://cltl.nl/leolani/friends/piek-1"},
        "utterance": "Bram is from the Netherlands",
        "utterance_type": UtteranceType.STATEMENT,
        "position": "0-25",
        "subject": {"label": "bram", "type": ["person"], "uri": "http://cltl.nl/leolani/world/bram-1"},
        "predicate": {"label": "be-from", "uri": "http://cltl.nl/leolani/n2mu/be-from"},
        "object": {"label": "netherlands", "type": ["location"], "uri": "http://cltl.nl/leolani/world/netherlands"},
        "perspective": {"certainty": 1, "polarity": 1, "sentiment": 0},
        "timestamp": datetime.combine(start_date, datetime.now().time()),
        "context_id": context_id,
    },
    {
        "chat": 1,
        "turn": 3,
        "author": {"label": "piek", "type": ["person"], "uri": "http://cltl.nl/leolani/friends/piek-1"},
        "utterance": "Selene is from Mexico",
        "utterance_type": UtteranceType.STATEMENT,
        "position": "0-25",
        "subject": {"label": "selene", "type": ["person"], "uri": "http://cltl.nl/leolani/world/selene-1"},
        "predicate": {"label": "be-from", "uri": "http://cltl.nl/leolani/n2mu/be-from"},
        "object": {"label": "mexico", "type": ["location"], "uri": "http://cltl.nl/leolani/world/mexico"},
        "perspective": {"certainty": 1, "polarity": 1, "sentiment": 0},
        "timestamp": datetime.combine(start_date, datetime.now().time()),
        "context_id": context_id,
    },
]

# Question capsules follow the same shape as statement capsules, but leave the unknown slot
# (subject, object, or both) with an empty label/uri so cltl.brain treats it as a wildcard.
question_capsules = [
    {
        "chat": 1,
        "turn": 4,
        "author": {"label": "joey", "type": ["person"], "uri": "http://cltl.nl/leolani/friends/joey-1"},
        "utterance": "Where is Bram from?",
        "utterance_type": UtteranceType.QUESTION,
        "position": "",
        "subject": {"label": "bram", "type": ["person"], "uri": "http://cltl.nl/leolani/world/bram-1"},
        "predicate": {"label": "be-from", "uri": "http://cltl.nl/leolani/n2mu/be-from"},
        "object": {"label": "", "type": [""], "uri": ""},
        "timestamp": datetime.combine(start_date, datetime.now().time()),
        "context_id": context_id,
    },
    {
        "chat": 1,
        "turn": 5,
        "author": {"label": "joey", "type": ["person"], "uri": "http://cltl.nl/leolani/friends/joey-1"},
        "utterance": "Who is from Serbia?",
        "utterance_type": UtteranceType.QUESTION,
        "position": "",
        "subject": {"label": "", "type": ["person"], "uri": ""},
        "predicate": {"label": "be-from", "uri": "http://cltl.nl/leolani/n2mu/be-from"},
        "object": {"label": "serbia", "type": ["location"], "uri": "http://cltl.nl/leolani/world/serbia"},
        "timestamp": datetime.combine(start_date, datetime.now().time()),
        "context_id": context_id,
    },
    {
        "chat": 1,
        "turn": 6,
        "author": {"label": "joey", "type": ["person"], "uri": "http://cltl.nl/leolani/friends/joey-1"},
        "utterance": "Is Selene from Mexico?",
        "utterance_type": UtteranceType.QUESTION,
        "position": "",
        "subject": {"label": "selene", "type": ["person"], "uri": "http://cltl.nl/leolani/world/selene-1"},
        "predicate": {"label": "be-from", "uri": "http://cltl.nl/leolani/n2mu/be-from"},
        "object": {"label": "mexico", "type": ["location"], "uri": "http://cltl.nl/leolani/world/mexico"},
        "timestamp": datetime.combine(start_date, datetime.now().time()),
        "context_id": context_id,
    },
]


def main(address, log_path, out_path):
    # Connect to the GraphDB repository
    brain = LongTermMemory(address=address, log_dir=log_path, clear_all=False)

    # Create the context and add the facts we are going to ask about
    brain.capsule_context(context_capsule)
    for capsule in statement_capsules:
        brain.capsule_statement(capsule, reason_types=True, create_label=True)

    # Ask the brain the questions and inspect the results
    responses = []
    for capsule in question_capsules:
        print(f"\n---------------------------------------------------------------")
        print(f"Q: {capsule['utterance']}")

        result = brain.query_brain(capsule)
        bindings = result["response"]

        if not bindings:
            print("A: I don't know")
        else:
            for binding in bindings:
                subject_label = binding.get("slabel", {}).get("value", capsule["subject"]["label"])
                object_label = binding.get("olabel", {}).get("value", capsule["object"]["label"])
                print(f"A: {subject_label} {capsule['predicate']['label']} {object_label}")

        responses.append(brain_response_to_json(result))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(responses, f, indent=2)
    print(f"\nSaved {len(responses)} responses to {out_path}")


if __name__ == "__main__":
    kg = "http://localhost:7200/repositories/sandbox"
    kg = "http://localhost:7200/repositories/diabetes_event_details_and_types"
    parser = argparse.ArgumentParser(description="Query a GraphDB knowledge graph via cltl.brain")
    parser.add_argument("--address", type=str, default=kg,
                        help="Address of the GraphDB repository to query")
    parser.add_argument("--logs", type=str,
                        help="Directory to store the brain log files. Defaults to a temporary directory.")
    parser.add_argument("--out", type=str, default="./data/brain_responses/query_brain-responses.json",
                        help="File to save the query responses to")
    args, _ = parser.parse_known_args()

    if args.logs:
        main(args.address, Path(args.logs), Path(args.out))
    else:
        with TemporaryDirectory(prefix="brain-log") as log_path:
            main(args.address, Path(log_path), Path(args.out))
