# purple-log-parser

## Usage

Just create Parser instance and pass through path to logs like this:

```python
from parser import Parser


parser = Parser('~/.purple/logs/jabber/<my-jid>/<contact-jid>/')
```

after this you can access messages like this:

```python
# Iterate over all chat sessions and messages:
for session in parser.sessions:
    print 'session contact:', session.contact
    print 'session start:', session.start_dt
    for msg in session.messages:
        print 'Message contact:', msg.contact
        print 'Message time:   ', msg.time
        print 'Message text:   ', msg.text

# Or just like this:
for msg in parser.iter_messages():
    print 'Message contact:', msg.contact
    print 'Message time:   ', msg.time
    print 'Message text:   ', msg.text

```

Messages sorted by date and time.
