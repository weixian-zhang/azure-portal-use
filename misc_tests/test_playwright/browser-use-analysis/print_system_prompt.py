import os
import pprint

path = os.path.join(os.path.dirname(__file__), 'browser-use-input-message-user-message.md')
with open(path, "rb") as f:
    content = f.read()
    pprint.pprint(content.decode('utf-8'))