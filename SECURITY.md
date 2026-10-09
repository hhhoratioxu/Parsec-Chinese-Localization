# Security policy

This companion is an experimental third-party tool. It does not patch Parsec binaries, modify authentication, settings files, network/stream protocols or drivers. It does not request elevation or add a service.

Live reads require a verified Windows executable, known application version, known UI version and recognizable WebView structure. Only known public labels and allowlisted parameter values are retained. Edit controls, host names, account text, device names, unknown values and raw trees are not persisted. Logs accept fixed event names only. The update checker contacts the fixed public GitHub endpoint only after a user click.

Please report a vulnerability through the repository's private security reporting feature if available. If it is unavailable, open an issue describing the category and asking for a private contact, without publishing exploit details, credentials or personal logs. There is no promise of a response deadline. Never paste Parsec tokens or user.bin.

Unsigned installers are accurately disclosed. No instructions to disable security, signature verification or Gatekeeper are permitted. Build status does not establish application integration or streaming safety under all workloads.
