# Jarvis Runtime — Available Commands

This file documents the commands currently available in the active runtime (`main.py`).

## Runtime Modes
- Default mode: **terminal**
- Start terminal mode: `python main.py`
- Start voice mode directly: `python main.py --voice`
- Switch mode commands:
  - `switch to voice`
  - `switch to terminal`
- Stop runtime: `exit`
- Stop current speech: `stop` or `shut up`
- Wake acknowledgement: `jarvis`
- Sleep voice session (back to wake-word listening): `sleep`

## System Commands
| Command | Description |
|---|---|
| `jarvis` | Wake/acknowledge prompt |
| `sleep` | Puts voice loop back to wake-word listening |
| `exit` | Stops runtime |
| `enable auto start` | Enable Windows auto-start |
| `disable auto start` | Disable Windows auto-start |
| `health check` | Runtime health and stats |

## Time Commands
| Command | Description |
|---|---|
| `time`, `what time` | Current time |
| `date`, `what date` | Current date |
| `day`, `what day` | Current weekday |
| `year` | Current year |

## Web & App Commands
| Command | Description |
|---|---|
| `open youtube` | Open YouTube |
| `search <query>` | Web search |
| `go to <site>` | Open website |
| `open <app>` / `launch <app>` / `start <app>` | Open local app |
| `open gh` | Opens GitHub alias |
| `open gmail` / `open mail` | Opens Gmail |

Notes:
- App launching supports built-in aliases (notepad, chrome, vscode, spotify, discord, slack, notion, whatsapp, tlauncher, etc.).
- You can add custom aliases in `config/config.json`:
```json
{
  "app_aliases": {
    "tlauncher": "C:\\\\Path\\\\To\\\\TLauncher.exe",
    "notion": "C:\\\\Users\\\\<you>\\\\AppData\\\\Local\\\\Programs\\\\Notion\\\\Notion.exe"
  }
}
```
- Runtime alias management commands:
  - `add app alias <name> <full_path_or_executable>`
  - `remove app alias <name>`
  - `list app aliases`

## Timer & Reminder Commands
| Command | Description |
|---|---|
| `set timer for <N> minutes/seconds/hours` | Set timer |
| `check timer`, `timer status`, `how much time` | Check active timer |
| `cancel timer`, `stop timer` | Cancel active timer |
| `remind me in <N> minutes to <message>` | Create reminder |

## Task Commands
| Command | Description |
|---|---|
| `add task <text>` | Add task |
| `list tasks`, `show tasks`, `what are my tasks` | List pending tasks |
| `complete task <id>`, `finish task <id>` | Complete task |
| `delete task <id>`, `remove task <id>` | Delete task |
| `what was i doing`, `last task` | Last pending task |

## Macro Commands
| Command | Description |
|---|---|
| `create macro <name> <actions>` | Create macro |
| `<macro name>` | Execute macro |
| `list macros` | List macros |
| `delete macro <name>` | Delete macro |

## Screenshot & Clipboard
| Command | Description |
|---|---|
| `screenshot`, `take screenshot` | Capture screenshot |
| `read clipboard` | Read clipboard text |
| `copy <text>`, `paste` | Clipboard actions |

## Memory Commands
| Command | Description |
|---|---|
| `remember that <fact>` | Store memory |
| `what do you remember`, `list memories` | List memories |
| `delete memory <id>` | Delete memory by ID |

## Productivity & Focus
| Command | Description |
|---|---|
| `good morning`, `morning briefing` | Daily briefing |
| `enter focus mode` | Enable focus mode |
| `exit focus mode` | Disable focus mode |
| `focus for <N> minutes` | Timed focus session |
| `start work session` | Start session tracking |
| `end work session` | End session tracking |
| `how long have i worked` | Work duration today |

## Analytics
| Command | Description |
|---|---|
| `show analytics`, `productivity report`, `performance stats` | Analytics report |

## AI / Document Commands
| Command | Description |
|---|---|
| `draft ...`, `research ...`, `plan ...`, `notes ...`, `code ...` | AI generation |
| `explain ...`, `what is ...`, `tell me about ...` | AI explanation |
| `more`, `tell me more`, `explain more` | Continue prior AI output |
| `save it`, `save that`, `create document` | Save last AI output |
| `save as <filename>` | Save last AI output as text |
| `confirm`, `proceed`, `yes` | Confirm guarded AI file generation |

## Multi-Agent Additions
These are also supported through the orchestrator fallback when legacy router does not resolve:
- `research <topic>`
- `summarize <text>`
- `answer <question>`
- code intents like `generate_code`, `fix_code`, `explain_code`, `write_script`

## Parsing
Jarvis supports multi-command chaining using:
- `and`
- `then`
- `also`
- `,`

Example:
- `open youtube and set timer for 5 minutes`
