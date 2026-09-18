"""Run a complete local blind round without a browser or an external model."""

from conversation import Conversation
from experiment import ExperimentStore


if __name__ == '__main__':
    store = ExperimentStore(Conversation())
    session_id, human_invite = store.create('turing_1936', 'blind')
    store.ask(session_id, 'What did you publish about computable numbers?')
    store.answer_human(human_invite, 'The supplied record mentions a paper on computable numbers.')
    blind = store.view(session_id)
    print(blind['rounds'][0])
    print(store.reveal(session_id, 'A', 60)['verdict'])
    print('Demo only: the human answer above is a scripted fixture, not a real participant.')
