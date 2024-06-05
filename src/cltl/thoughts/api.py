from cltl.commons.casefolding import (casefold_capsule)

from cltl.thoughts.thought_selection import logger
from cltl.thoughts.thought_selection.utils.thought_utils import thoughts_from_brain


class ThoughtSelector(object):

    def __init__(self):
        # type: () -> None
        """
        Select one of the given thoughts to generate a response

        Parameters
        ----------
        """

        self._log = logger.getChild(self.__class__.__name__)
        self._log.info("Booted")

        # infrastructure to keep track of selections
        self._last_thought = None

    @property
    def last_thought(self):
        return self._last_thought

    def _preprocess(self, brain_response, thought_options=None):
        # Manage types of capsules
        capsule_type = 'statement' if 'statement' in brain_response.keys() else 'mention'
        capsule_focus = 'triple' if 'statement' in brain_response.keys() else 'entity'

        # Quick check if there is anything to do here
        if not brain_response[capsule_type][capsule_focus]:
            return None

        # What types of thoughts will we phrase?
        if not thought_options:
            thought_options = ['_complement_conflict', '_negation_conflicts',
                               '_statement_novelty', '_entity_novelty',
                               '_subject_gaps', '_complement_gaps',
                               '_overlaps', '_trust'] if 'statement' in brain_response.keys() \
                else ['_entity_novelty', '_complement_gaps']
        self._log.debug(f'Thoughts options: {thought_options}')

        # Casefold
        thoughts = casefold_capsule(brain_response['thoughts'], format='natural')
        utterance = casefold_capsule(brain_response[capsule_type], format='natural')

        # Extract thoughts from brain response
        thoughts = thoughts_from_brain(utterance, thoughts, filter=thought_options)

        return thoughts

    def _postprocess(self, all_thoughts, selected_thought):
        # Keep track of selections
        self._last_thought = selected_thought
        thought_type, thought_info = all_thoughts[self._last_thought]
        self._log.info(f"Chosen thought type: {thought_type}")

        # Preprocess thought_info and utterance (triples)
        thought_info = casefold_capsule(thought_info, format="natural")

        return thought_type, thought_info

    def select(self, options):
        raise NotImplementedError()
