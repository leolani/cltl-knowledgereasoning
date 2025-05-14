from rdflib import ConjunctiveGraph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

from cltl.thoughts.thought_selection.rl_model.metrics.graph_measures import get_avg_degree, get_sparseness, \
    get_shortest_path, get_count_nodes, get_count_edges
from cltl.thoughts.thought_selection.rl_model.metrics.ontology_measures import get_avg_population


class BrainEvaluator(object):
    def __init__(self, brain, main_graph_metric):
        """ Create an object to evaluate the state of the brain according to different graph metrics.
        The graph can be evaluated by a single given metric, or a full set of pre established metrics
        """
        self._brain = brain
        self.metric = main_graph_metric

    def brain_as_graph(self):
        # Take brain from previous episodes
        graph = ConjunctiveGraph()
        graph.parse(data=self._brain._connection.export_repository(), format='trig')

        return graph

    def brain_as_netx(self):
        # Take brain from previous episodes
        netx = rdflib_to_networkx_multidigraph(self.brain_as_graph())

        return netx

    def evaluate_brain_state(self):
        brain_state = None

        ##### Group A #####
        if self.metric == 'Average degree':
            brain_state = get_avg_degree(self.brain_as_netx())
        elif self.metric == 'Sparseness':
            brain_state = get_sparseness(self.brain_as_netx())
        elif self.metric == 'Shortest path':
            brain_state = get_shortest_path(self.brain_as_netx())

        ##### Group B #####
        if self.metric == 'Total triples':
            brain_state = self._brain.count_triples()
        elif self.metric == 'Average population':
            brain_state = get_avg_population(self.brain_as_graph())

        ##### Group C #####
        elif self.metric == 'Ratio claims to triples':
            brain_state = self._brain.count_statements() / self._brain.count_triples()
        elif self.metric == 'Ratio perspectives to claims':
            if self._brain.count_statements() != 0:
                brain_state = self._brain.count_perspectives() / self._brain.count_statements()
            else:
                brain_state = self._brain.count_perspectives() / 0.0000001
        elif self.metric == 'Ratio conflicts to claims':
            if self._brain.count_statements() != 0:
                brain_state = len(self._brain.get_all_negation_conflicts()) / self._brain.count_statements()
            else:
                brain_state = len(self._brain.get_all_negation_conflicts()) / 0.0000001

        return brain_state

    @staticmethod
    def compare_brain_states(current_state, prev_state):
        # TODO standardize according to metric
        if current_state is None or prev_state is None or prev_state == 0:
            reward = 0
        else:
            reward = current_state / prev_state
            # shift so we have negative rewards and we punish for shrinking
            reward -= 1

        return reward

    def calculate_brain_statistics(self, brain_response):
        # Grab the thoughts
        thoughts = brain_response['thoughts']

        # Gather basic stats
        stats = {
            'turn': brain_response['statement']['turn'],

            'cardinality conflicts': len(thoughts['_complement_conflict']) if thoughts['_complement_conflict'] else 0,
            'negation conflicts': len(thoughts['_negation_conflicts']) if thoughts['_negation_conflicts'] else 0,
            'subject gaps': len(thoughts['_subject_gaps']) if thoughts['_subject_gaps'] else 0,
            'object gaps': len(thoughts['_complement_gaps']) if thoughts['_complement_gaps'] else 0,
            'statement novelty': len(thoughts['_statement_novelty']) if thoughts['_statement_novelty'] else 0,
            'subject novelty': int(thoughts['_entity_novelty']['_subject']['value']),
            'object novelty': int(thoughts['_entity_novelty']['_complement']['value']),
            'overlaps subject-predicate': len(thoughts['_overlaps']['_subject'])
            if thoughts['_overlaps']['_subject'] else 0,
            'overlaps predicate-object': len(thoughts['_overlaps']['_complement'])
            if thoughts['_overlaps']['_complement'] else 0,
            'trust': thoughts['_trust'],

            ##### Group A #####
            'Total nodes': get_count_nodes(self.brain_as_netx()),
            'Total edges': get_count_edges(self.brain_as_netx()),
            'Average degree': get_avg_degree(self.brain_as_netx()),
            'Sparseness': get_sparseness(self.brain_as_netx()),
            'Shortest path': get_shortest_path(self.brain_as_netx()),

            ##### Group B #####
            'Total triples': self._brain.count_triples(),
            'Total classes': len(self._brain.get_classes()),
            'Total predicates': len(self._brain.get_predicates()),
            'Average population': get_avg_population(self.brain_as_graph()),

            ##### Group C #####
            'Total claims': self._brain.count_statements(),
            'Total perspectives': self._brain.count_perspectives(),
            'Total conflicts': len(self._brain.get_all_negation_conflicts()),
            'Total sources': self._brain.count_friends(),
        }

        # Compute composite stats
        stats['Ratio claims to triples'] = stats['Total claims'] / stats['Total triples']
        stats['Ratio perspectives to triples'] = stats['Total perspectives'] / stats['Total triples']
        stats['Ratio conflicts to triples'] = stats['Total conflicts'] / stats['Total triples']
        stats['Ratio perspectives to claims'] = stats['Total perspectives'] / stats['Total claims']
        stats['Ratio conflicts to claims'] = stats['Total conflicts'] / stats['Total claims']

        return stats
