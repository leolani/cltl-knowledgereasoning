""" Filename:     thought_utils.py
    Author(s):    Thomas Bellucci, Selene Baez Santamaria
    Description:  Utility functions used by the RLReplier defined in
                  Replier.py.
    Date created: Nov. 11th, 2021
    Date updated: Nov. 9th, 2022
"""

from collections import defaultdict

import random
from itertools import combinations


def separate_select_negation_conflicts(conflicts):
    affirmative_conflict = [item for item in conflicts if item['_polarity_value'] == 'POSITIVE']
    negative_conflict = [item for item in conflicts if item['_polarity_value'] == 'NEGATIVE']

    # TODO smarter selection here, by same author or same period of time?
    affirmative_conflict = random.choice(affirmative_conflict) if affirmative_conflict else []
    negative_conflict = random.choice(negative_conflict) if negative_conflict else []

    return affirmative_conflict, negative_conflict


def thoughts_from_brain(utt, cap, filter=None):
    """Takes thoughts and extracts thought types end entity types of the entities involved,  in the form of
    a dictionary, e.g. {'object_gap person book':('_object_gap', thought_dict), ...}.

    params
    dict capsule: dict containing the input utterance, triples, perspectives
                  and contextual information (e.g. location, speaker)
    object typer: Typing object that maps a token to a type (a hypernym).

    returns:      dict mapping from thought names to (thought_type, thought_info)
    """

    # Trust is always available
    thoughts = dict()
    if "_trust" in filter:
        thoughts["_trust"] = ("_trust", {"value": cap["_trust"]})

    if "_statement_novelty" in filter:
        # Any statement novelties? (can always be called!)
        if cap["_statement_novelty"]:  # == previous claims!
            thoughts["no_statement_novelty"] = ("_statement_novelty", {"provenance": cap["_statement_novelty"]})
        else:
            thoughts["statement_novelty"] = ("_statement_novelty", {"provenance": cap["_statement_novelty"]})

    if "_overlaps" in filter:
        # Any single overlap?, e.g. 'overlap animal'
        if cap["_overlaps"]["_subject"]:
            for overlap in cap["_overlaps"]["_subject"]:
                overlap_name = "overlap -subj %s" % overlap["_entity"]["_types"][-1]
                thoughts[overlap_name] = ("_overlaps", {"_subject": [overlap], "_complement": []})

        if cap["_overlaps"]["_complement"]:
            for overlap in cap["_overlaps"]["_complement"]:
                overlap_name = "overlap -compl %s" % overlap["_entity"]["_types"][-1]
                thoughts[overlap_name] = ("_overlaps", {"_subject": [], "_complement": [overlap]})

        # Any pairs of overlaps?, e.g. 'overlap animal person'
        if cap["_overlaps"]["_subject"]:
            for overlaps in combinations(cap["_overlaps"]["_subject"], r=2):
                entities = sorted([overlaps[0]["_entity"]["_types"][-1], overlaps[1]["_entity"]["_types"][-1]])
                overlap_name = "overlap -subj %s %s" % (entities[0], entities[1])
                thoughts[overlap_name] = ("_overlaps", {"_subject": overlaps, "_complement": []})

        if cap["_overlaps"]["_complement"]:
            for overlaps in combinations(cap["_overlaps"]["_complement"], r=2):
                entities = sorted([overlaps[0]["_entity"]["_types"][-1], overlaps[1]["_entity"]["_types"][-1]])
                overlap_name = "overlap -compl %s %s" % (entities[0], entities[1])
                thoughts[overlap_name] = ("_overlaps", {"_subject": [], "_complement": overlaps})

    if "_entity_novelty" in filter:
        # Any entity novelties?
        if cap["_entity_novelty"]["_subject"] == "True":
            entity = utt["triple"]["_subject"] if 'triple' in utt.keys() else utt["entity"]
            novelty_name = ("entity_novelty -subj %s" % entity["_types"][0])
            thoughts[novelty_name] = ("_entity_novelty", {"_subject": True, "_complement": False})

        if cap["_entity_novelty"]["_complement"] == "True":
            entity = utt["triple"]["_complement"] if 'triple' in utt.keys() else utt["entity"]
            novelty_name = ("entity_novelty -compl %s" % entity["_types"][0])
            thoughts[novelty_name] = ("_entity_novelty", {"_subject": False, "_complement": True})

        # Alternative, if there are no novel entities
        thoughts["entity_novelty -none"] = ("_entity_novelty", {"_subject": False, "_complement": False})

    if "_subject_gaps" in filter:
        # Any subject gaps?, e.g. 'subject_gap person animal'
        if cap["_subject_gaps"]["_subject"]:
            for gap in cap["_subject_gaps"]["_subject"]:
                gap_name = "subject_gap -subj %s %s" % (
                    gap["_known_entity"]["_types"][0], gap["_target_entity_type"]["_types"][0])
                thoughts[gap_name] = ("_subject_gaps", {"_subject": [gap], "_complement": []})

        if cap["_subject_gaps"]["_complement"]:
            for gap in cap["_subject_gaps"]["_complement"]:
                gap_name = "subject_gap -compl %s %s" % (
                    gap["_known_entity"]["_types"][0], gap["_target_entity_type"]["_types"][0])
                thoughts[gap_name] = ("_subject_gaps", {"_subject": [], "_complement": [gap]})

        # Alternative, if there is no subject gap
        thoughts["subject_gap -none"] = ("_subject_gaps", {"_subject": [], "_complement": []})

    if "_complement_gaps" in filter:
        # any object gaps?, e.g. 'object_gap person animal'
        if cap["_complement_gaps"]["_subject"]:
            for gap in cap["_complement_gaps"]["_subject"]:
                gap_name = "object_gap -subj %s %s" % (
                    gap["_known_entity"]["_types"][0], gap["_target_entity_type"]["_types"][-1])
                thoughts[gap_name] = ("_complement_gaps", {"_subject": [gap], "_complement": []})

        if cap["_complement_gaps"]["_complement"]:
            for gap in cap["_complement_gaps"]["_complement"]:
                gap_name = "object_gap -compl %s %s" % (
                    gap["_known_entity"]["_types"][0], gap["_target_entity_type"]["_types"][-1])
                thoughts[gap_name] = ("_complement_gaps", {"_subject": [], "_complement": [gap]})

        # Alternative, if there is no object gap
        thoughts["object_gap -none"] = ("_complement_gaps", {"_subject": [], "_complement": []})

    if "_complement_conflict" in filter:
        # Any complement conflicts (cardinality conflict)?
        if cap["_complement_conflict"]:
            thoughts["complement_conflict"] = ("_complement_conflict", {"provenance": cap["_complement_conflict"][:1]})

    if "_negation_conflicts" in filter:
        # A negation conflict?
        if cap["_negation_conflicts"]:
            positives = [item for item in cap["_negation_conflicts"] if item["_polarity_value"] == "POSITIVE"]
            negatives = [item for item in cap["_negation_conflicts"] if item["_polarity_value"] == "NEGATIVE"]

            if positives and negatives:
                conflict_info = [random.choice(positives), random.choice(negatives)]
                thoughts["negation_conflict"] = ("_negation_conflicts", {"provenance": conflict_info})

    # Scramble to break ordering!
    thoughts = list(thoughts.items())
    random.shuffle(thoughts)
    return dict(thoughts)


def decompose_thoughts(utt, cap, filter=None):
    """Takes thoughts and extracts thought types end entity types of the entities involved, in a standard form of
    a dictionary, e.g. {'object_gap person book':('_object_gap', thought_dict), ...}.

    params
    dict utt: dict containing the input utterance, triples, perspectives
                  and contextual information (e.g. location, speaker)
    dict cap: dict containing the generated thoughts.

    returns:      nested dict mapping from thought names to (thought_type, thought_info)
    """
    thoughts = []
    if "_complement_conflict" in filter:
        # Any complement conflicts (cardinality conflict)?
        if cap["_complement_conflict"]:
            conflicts = cap["_complement_conflict"]

            for conflict in conflicts:  # == previous claims!
                info = gather_entity_type_info(conflict)
                info = gather_entity_type_info(conflict["_provenance"], info)

                element = {"thought_type": "_complement_conflict",
                           "entity_types": info,
                           "thought_info": conflict,
                           "extra_info": None}
                thoughts.append(element)

    if "_negation_conflicts" in filter:
        # A negation conflict?
        if cap["_negation_conflicts"]:
            conflicts = cap["_negation_conflicts"]

            # Select one positive and one negative here to ensure there is a conflict
            affirmative_conflict, negative_conflict = separate_select_negation_conflicts(conflicts)
            conflicts = [affirmative_conflict, negative_conflict]

            if len(conflicts) > 2:
                info = defaultdict(int)
                for n in conflicts:  # == previous claims!
                    info = gather_entity_type_info(n["_provenance"], info)

                element = {"thought_type": "_negation_conflicts",
                           "entity_types": info,
                           "thought_info": conflicts,
                           "extra_info": None}
                thoughts.append(element)

    if "_statement_novelty" in filter:
        # Any statement novelties? (can always be called!)
        novelty = cap["_statement_novelty"]

        for n in novelty:  # == previous claims!
            element = {"thought_type": "_statement_novelty",
                       "entity_types": gather_entity_type_info(n["_provenance"]),
                       "thought_info": n,
                       "extra_info": random.choice(['_subject', '_complement'])}
            thoughts.append(element)

    if "_entity_novelty" in filter:
        # Any entity novelties?
        if cap["_entity_novelty"]["_subject"]["value"] in ["True", True]:
            novelty = cap["_entity_novelty"]["_subject"]
            element = {"thought_type": "_entity_novelty",
                       "entity_types": gather_entity_type_info(novelty),
                       "thought_info": novelty,
                       "extra_info": "_subject"}
            thoughts.append(element)

        if cap["_entity_novelty"]["_complement"]["value"]  in ["True", True]:
            novelty = cap["_entity_novelty"]["_complement"]
            element = {"thought_type": "_entity_novelty",
                       "entity_types": gather_entity_type_info(novelty),
                       "thought_info": novelty,
                       "extra_info": "_complement"}
            thoughts.append(element)

    if "_subject_gaps" in filter:
        # Any subject gaps?, e.g. 'subject_gap person animal'
        if cap["_subject_gaps"]["_subject"]:
            for gap in cap["_subject_gaps"]["_subject"]:
                element = {"thought_type": "_subject_gaps",
                           "entity_types": gather_entity_type_info(gap),
                           "thought_info": gap,
                           "extra_info": "_subject"}
                thoughts.append(element)

        if cap["_subject_gaps"]["_complement"]:
            for gap in cap["_complement_gaps"]["_complement"]:
                element = {"thought_type": "_subject_gaps",
                           "entity_types": gather_entity_type_info(gap),
                           "thought_info": gap,
                           "extra_info": "_complement"}
                thoughts.append(element)

    if "_complement_gaps" in filter:
        # any object gaps?, e.g. 'object_gap person animal'
        if cap["_complement_gaps"]["_subject"]:
            for gap in cap["_complement_gaps"]["_subject"]:
                element = {"thought_type": "_complement_gaps",
                           "entity_types": gather_entity_type_info(gap),
                           "thought_info": gap,
                           "extra_info": "_subject"}
                thoughts.append(element)

        if cap["_complement_gaps"]["_complement"]:
            for gap in cap["_complement_gaps"]["_complement"]:
                element = {"thought_type": "_complement_gaps",
                           "entity_types": gather_entity_type_info(gap),
                           "thought_info": gap,
                           "extra_info": "_complement"}
                thoughts.append(element)

    if "_overlaps" in filter:
        # Any single overlap?, e.g. 'overlap animal'
        if cap["_overlaps"]["_subject"]:
            for overlap in cap["_overlaps"]["_subject"]:
                element = {"thought_type": "_overlaps",
                           "entity_types": gather_entity_type_info(overlap),
                           "thought_info": overlap,
                           "extra_info": "_subject"}
                thoughts.append(element)

        if cap["_overlaps"]["_complement"]:
            for overlap in cap["_overlaps"]["_complement"]:
                element = {"thought_type": "_overlaps",
                           "entity_types": gather_entity_type_info(overlap),
                           "thought_info": overlap,
                           "extra_info": "_complement"}
                thoughts.append(element)

    if "_trust" in filter:
        element = {"thought_type": "_trust",
                   "entity_types": {"Source": 1},
                   "thought_info": {"value": cap["_trust"]},
                   "extra_info": None}
        thoughts.append(element)

    # Scramble to break ordering!
    random.shuffle(thoughts)
    return thoughts


def gather_entity_type_info(thought_info, info=None):
    if not info:
        info = defaultdict(int)

    for entity, details in thought_info.items():
        if type(details) == dict and "_types" in details.keys():
            for typ in details["_types"]:
                info[typ] += 1

    return info
