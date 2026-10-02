# Contributor instructions

Keep credentials, subscription URLs, personal IP addresses and device paths out of this repository. Examples use placeholders supplied by the reader.
Document tested client versions and distinguish DNS privacy, fixed egress, residential classification and account status. Never promise zero disruption, anonymity or account safety.
Configuration helpers must default to reviewable plans, preserve unrelated routing and subscriptions, and avoid stopping a running network core or closing existing connections.
Read docs/HANDOFF.md for the current scope. Change only assigned files; validate behavior appropriate to the change and review automation before publication.

For helper changes: run `python3 -m unittest discover -s skills/flclash-ai-privacy/scripts/tests`.
For guide or site changes: install `requirements.txt`, then run `python3 scripts/build_site.py --config site.json`; verify the rendered pages and navigation.
Keep `site.json` as the source of mutable site metadata. Review public files for secrets and private data before pushing.
