## Command Overview

|               Command               | Description                                            |
| :---------------------------------: | ------------------------------------------------------ |
|               `!logs`               | attaches an archive of logs files to a discord message |
| [`!pg`](#database-dump-and-restore) | dump or restore the bot's database                     |

## Database Dump and Restore

The bot owner or one of the repository owners can back up DuckBot's database with `!pg dump`. DuckBot sends the gzipped dump to you in a direct message rather than posting it in the channel, since it holds everyone's saved weather locations.

> Human: !pg dump\
> DuckBot: Sent it to your DMs, brother.

Attach a dump to `!pg restore` to load it back in. This drops whatever is in the database and replaces it with the contents of the dump.

> Human: !pg restore (+duckbot.sql.gz)\
> DuckBot: Restored, brother.
