# Static Code Analysis — Issues

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| B605: Starting a process with a shell | Security — High | 43 | `os.system("cat " + file)` executes a shell command using a filename, potentially allowing command injection. | Removed `os.system()` and replaced it with Python's built-in file handling. |
| B110: Try, Except, Pass Detected | Code Quality — Low | 27–28 | A bare `except` followed by `pass` silently suppresses exceptions and hides unexpected errors. | Replaced the broad exception handler with an explicit check for a missing reservation ID. |
| C0301: Line too long | Code Style | 17 (original) | A line exceeded the recommended maximum length of 100 characters. | Split the line into shorter lines. |
| C0114: Missing module docstring | Code Quality | 1 | The module lacked a docstring describing its purpose. | Added a module-level docstring. |
| C0103: Invalid naming | Naming Convention | 8 (original) | The reservation counter name triggered a naming warning. | Replaced the global counter with a mutable counter dictionary. |
| C0116: Missing function docstrings | Code Quality | Multiple | Functions lacked docstrings explaining their purpose. | Added descriptive docstrings. |
| W0102: Dangerous default value | Bug Risk | 10 (original) | A mutable list was used as a default argument. | Changed the default to `None` and initialized a new list inside the function. |
| W0603: Global statement | Code Quality | 11 (original) | The function modified a global variable. | Used a mutable counter dictionary instead of a global statement. |
| C0206: Dictionary iteration | Code Quality | 12 (original) | The code iterated over dictionary keys to access values. | Used `.items()` to iterate over keys and values. |
| C0209: String formatting | Code Style | 14 (original) | Percent-style formatting was used instead of an f-string. | Replaced it with an f-string. |
| W0702: Bare except | Error Handling | 27 (original) | A bare exception handler suppressed errors. | Added explicit handling for missing reservation IDs. |
| W1514: Unspecified encoding | File Handling | 41 (original) | Files were opened without specifying an encoding. | Added `encoding="utf-8"`. |
| R1732: Resource management | Code Quality | 41 (original) | Files were opened without context managers. | Used `with open(...)` for safe resource handling. |
| C0103: Function naming | Naming Convention | 39 (original) | The function name did not follow snake_case. | Renamed it to `log_conflicts()`. |
| W0612: Unused variables | Code Quality | 56, 57, 59 (original) | Variables were assigned but never used. | Removed the unused assignments. |
| E302: Expected 2 blank lines | Formatting | 11, 22, 30, 34, 39, 45 | Top-level functions did not have the required blank-line spacing. | Added the required blank lines between functions. |
| E501: Line too long | Formatting | 14, 18 | Lines exceeded Flake8's 79-character limit. | Split long lines across multiple lines. |
| E722: Bare except | Error Handling | 27 | A bare exception handler was used. | Replaced it with explicit error handling. |
| F841: Unused local variables | Code Quality | 46, 47, 49 | Variables were assigned values but never used. | Removed unnecessary variable assignments. |
| E305: Expected 2 blank lines after function | Formatting | 59 | Insufficient blank lines appeared after a function definition. | Added the required blank-line spacing. |