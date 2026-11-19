# Typing Test

A simple desktop typing test made with Python and Tkinter. It uses only Python's standard library, so there are no packages to install.

## Run on Windows

1. Install Python 3 if it is not already installed. During setup, enable **Add Python to PATH**.
2. Double-click `run_typing_test.bat`, or open PowerShell in this folder and run:

   ```powershell
   py typing_test.py
   ```

If `py` is unavailable, use `python typing_test.py`.

## Run on Linux

Install Python 3 and the Tkinter system package if needed (often named `python3-tk`), then run:

```bash
python3 typing_test.py
```

## Using the app

- Type the displayed passage in the typing area. The timer starts on the first keystroke.
- WPM is based on correctly matched characters, with five characters counted as one word.
- Accuracy is the share of entered characters that match the passage at the same position.
- The attempt saves automatically when you finish the passage, or when you select **Finish attempt**.
- Select **New passage** to start another attempt.

Completed attempts are appended to `attempts.csv` in the user's application data folder:

- Windows: `%APPDATA%\TypingTest\attempts.csv`
- macOS: `~/Library/Application Support/TypingTest/attempts.csv`
- Linux: `$XDG_DATA_HOME/TypingTest/attempts.csv`, or `~/.local/share/TypingTest/attempts.csv` by default

The CSV includes the local date/time, WPM, accuracy, duration, and the text entered. It is stored locally on the computer.
