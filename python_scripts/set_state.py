entity_id = data.get('entity_id')
if not entity_id:
    logger.error('No entity_id provided')
state = data.get('state')
if not state:
    logger.error('No state provided')
hass.states.set(entity_id, state)

