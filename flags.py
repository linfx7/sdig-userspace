
# message type
NOTIFICATION = 0x80
CONFIGURATION = 0x40
QUERY = 0x20


# notification type
STATUS = 0x80
EVENT = 0x40
# event notification type
EVENT_PACKET = 0x80
EVENT_OVERLOAD = 0x40
EVENT_CRASH = 0x20
# status notification type


# configuration element type
ELEMENT_RULE = 0x80
ELEMENT_CONFIGURATION = 0x40
ELEMENT_SECRET = 0x20
# rule action
RULE_DISCARD = 0x80
RULE_BYPASS = 0x40
RULE_PROTECT = 0x20


# response message
ACK = 0x80
SUCCESS = 0x40
ERROR = 0x20