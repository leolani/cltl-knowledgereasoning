# TODO revise overlap with provenance
class StatementNovelty(object):
    def __init__(self, provenance):
        # type: (Provenance) -> None
        """
        Construct StatementNovelty Object
        Parameters
        ----------
        provenance: Provenance
            Information about who said the acquired information and when
        """
        self._provenance = provenance

    @property
    def provenance(self):
        # type: () -> Provenance
        return self._provenance

    @property
    def author(self):
        # type: () -> str
        return self._provenance.author

    @property
    def date(self):
        # type: () -> date
        return self._provenance.date

    def casefold(self, format='triple'):
        # type (str) -> ()
        """
        Format the labels to match triples or natural language
        Parameters
        ----------
        format

        Returns
        -------

        """
        self._provenance.casefold(format)

    def __repr__(self):
        return f'{self._provenance.__repr__()}'


class EntityNovelty(object):
    def __init__(self, existence_subject, existence_complement):
        # type: (bool, bool) -> None
        """
        Construct EntityNovelty Object
        Parameters
        ----------
        existence_subject: bool
            Truth value for determining if this subject is something new
        existence_complement: bool
            Truth value for determining if this complement is something new
        """
        self._subject = not existence_subject
        self._complement = not existence_complement

    @property
    def subject(self):
        # type: () -> bool
        return self._subject

    @property
    def complement(self):
        # type: () -> bool
        return self._complement

    def __repr__(self):
        subject = 'new' if self.subject else 'existing'
        complement = 'new' if self.complement else 'existing'
        return f'{subject} subject - {complement} object'
