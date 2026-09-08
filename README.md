# recycle-radarr
Python script to delete movies from Radarr with time add and whitelist

/!\ Always test dry-run before delete /!\

Replace the radarr url and the api key value according to your server

usage: recycle-radarr.py [-h] [--dry-run] [--days DAYS] [--whitelist WHITELIST]

Clean old movies in Radarr

options:
  -h, --help            show this help message and exit
  --dry-run             Mode test (don't delete anything)
  --days DAYS           Number of days
  --whitelist WHITELIST
                        whitelist file

Exemple :

./recycle-radarr.py --dry-run --days 365 --whitelist whitelist.txt

Create a file (e.g., whitelist.txt) with one movie title per line:
The Matrix
Inception
Interstellar

