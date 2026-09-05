# Local port snapshot

Checked: 2026-09-05 15:31:11 +08:00. Read-only TCP listener and process-name inspection.

Project port rechecked at 2026-09-05 15:45:07 +08:00: 8765 still not listening.

Project: `127.0.0.1:8765` was not listening. HTTP request to `/authoring/collision-pi-question-editor.html` was refused. The authoring page and question filter share this static service; no separate project port was found in project configuration. No services were started or stopped during this inspection.

Other TCP listeners (duplicate IPv4/IPv6 bindings grouped):

| Ports | Process | Status |
| --- | --- | --- |
| 135, 5040, 7680, 28317, 49666, 49667 | svchost | Listening |
| 139, 445, 5357 | System | Listening |
| 902, 912 | vmware-authd | Listening |
| 8475 | baidunetdiskhost | Listening |
| 9080, 15000, 54321 | DownloadSDKServer | Listening |
| 9081, 10584, 15001, 54322 | thunder | Listening |
| 10000 | YunDetectService | Listening |
| 10572, 21603 | xllite | Listening |
| 22306, 22307 | fotiaoqiang | Listening |
| 22308 | ss-local | Listening |
| 27036, 65327, 65329 | steam | Listening |
| 42050 | OneDrive.Sync.Service | Listening |
| 49664 | lsass | Listening |
| 49665 | wininit | Listening |
| 49668 | spoolsv | Listening |
| 49669 | jhi_service | Listening |
| 49670 | services | Listening |
| 49713 | svchost | Listening |
| 52443 | HipsDaemon | Listening |

Listening status does not certify application health. Only the project HTTP endpoint was probed; unrelated services were not interacted with.
