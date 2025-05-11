import random

from cltl.thoughts.api import ThoughtSelector

EMPTY_THOUGHT_OPTIONS = {'_complement_conflict': [], '_negation_conflicts': [],
                   '_statement_novelty': [], '_entity_novelty': {},
                   '_subject_gaps': {}, '_complement_gaps': {},
                   '_overlaps': {}, '_trust': None}


class PerTypeSelector(ThoughtSelector):
    def __init__(self, thought_type="_subject_gaps"):
        """
        Initializes the most basic selector, choosing randomly amongst thoughts
        :param randomness:
        :param priority:
        """
        super().__init__()

        self._thought_type = thought_type

    def select(self, thoughts):
        thoughts = self._preprocess(thoughts, thought_options=[self._thought_type])

        if thoughts:
            selected_thought = random.choice(list(thoughts))

            # Safe processing
            thought_type, thought_info = self._postprocess(thoughts, selected_thought)
            return {self._thought_type: thought_info}

        else:
            return {self._thought_type: EMPTY_THOUGHT_OPTIONS[self._thought_type]}


if __name__ == '__main__':
    s = PerTypeSelector()
    print(s.select(['b', 'a']))
