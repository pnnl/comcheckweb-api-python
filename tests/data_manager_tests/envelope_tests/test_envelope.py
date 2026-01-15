from comcheck_api.types.core_types import *

def test_append_subcomponent(envelope: Envelope, ag_wall: AgWall):
    envelope.append_subcomponent(ag_wall)

    assert len(envelope.agWall) == 1

def test_remove_from_subcomponent_list(envelope: Envelope, ag_wall: AgWall):
    envelope.append_subcomponent(ag_wall)
    envelope.remove_from_subcomponent_list(subcomponent=ag_wall)

    assert len(envelope.agWall) == 0