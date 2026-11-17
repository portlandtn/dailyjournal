Daily Journal
=============

A morning and evening journal you run from the terminal.

Start here
----------
1. Open a terminal in this folder.
     Windows: open the folder, click the address bar, type  cmd  and press Enter.
     Mac:     right-click the folder and choose "New Terminal at Folder".
     Linux:   right-click the folder and choose "Open in Terminal".
2. Run setup once:
     Windows:    dailyjournal setup
     Mac/Linux:  ./dailyjournal setup
3. Each morning:   dailyjournal am
   Each evening:   dailyjournal pm
   Any time:       dailyjournal append "a quick note"
   Look back:      dailyjournal last

On Windows you can also double-click dailyjournal.exe and type commands
into the window that opens.

Which edition is this?
----------------------
Run  dailyjournal help  and read the last line.

- No-AI edition: never asks for an API key and never connects to the internet.
- OpenAI edition: if you add an OpenAI API key in setup, your answers are
  sent to OpenAI to produce the summary. Without a key it behaves like the
  no-AI edition.

Your journal is stored on this computer. Setup shows you where.

Security warnings
-----------------
Windows: "Windows protected your PC" appears because the download is not
code-signed. Click "More info", then "Run anyway".

Mac: if macOS refuses to open it, open System Settings > Privacy & Security,
scroll down, and click "Open Anyway" next to dailyjournal.

Linux: if you see "Permission denied", run:  chmod +x dailyjournal

More: https://jedmay.com/tools/daily-journal
Source and license: https://github.com/portlandtn/dailyjournal
