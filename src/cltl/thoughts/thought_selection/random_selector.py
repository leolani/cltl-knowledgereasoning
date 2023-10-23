import random

from cltl.thoughts.api import ThoughtSelector


class RandomSelector(ThoughtSelector):
    def __init__(self, randomness=1.0, priority=()):
        """
        Initializes the most basic selector, choosing randomly amongst thoughts
        :param randomness:
        :param priority:
        """
        super().__init__()

        self._randomness = randomness
        self._priority = {type: idx for idx, type in enumerate(priority)}

    def select(self, thoughts):
        thoughts = self._preprocess(thoughts)

        if random.random() < self._randomness:
            selected_thought = random.choice(list(thoughts))

        else:
            selected_thought = filter(None, sorted(thoughts, key=self._get_order))[0]

        # Safe processing
        thought_type, thought_info = self._postprocess(thoughts, selected_thought)
        return {thought_type: thought_info}

    def _get_order(self, thought):
        if thought not in self._priority:
            return float('inf')

        return self._priority[thought]


if __name__ == '__main__':
    s = RandomSelector(randomness=0.5, priority=['a', 'b'])
    print(s.select(['b', 'a']))
