Really simplistic script to distribute queued prompts.

Takes a primary node and 1 or more secondary nodes, when it sees the primary has >0 pending in queue it tries to move them to idle secondary nodes.

python3 queueshare.py http://primary:8188 http://secondary1:8188 http://secondary2:8188 ...

Added "random", if you use random as the first word then it will randomly pull a prompt from the first server instead of the first in queue

Notes:

Must have been started with --listen if on different IP addresses.

Custom nodes, checkpoints, loras etc must match.

No intelligence is done with output files, they're just stored locally on each node.

