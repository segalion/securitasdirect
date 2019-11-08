entity_id = data.get('entity_id')
if not entity_id:
    logger.error('No entity_id provided')
state = data.get('state')
if state:
    hass.states.set(entity_id, state)
state_attributes = data.get('state_attributes')
