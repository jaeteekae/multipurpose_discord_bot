This bot only works in a single server, and it is meant for use amongst a group of Trusted Individuals who won't abuse its power. Commands also work through DM.

## Bot Commands:

#### Out of Office
`!away <message>` - sets you away so that other people get shown your away `message` when they @mention you in the chat

`!back` - removes the away marker

#### Gif Dictionary
`!gif-add <shortcut> <gif url | uploaded gif>` - downloads the gif and adds it to the dictionary under `shortcut`

`!gif-list [filter]` - returns a list of all the gifs in the dictionary (that contain the phrase `filter` when provided). DMs the list if it's longer than 10 gifs

`!gif-remove <shortcut>` - removes the gif from the dictionary

`!gif-rename <old shortcut> <new shortcut>` - renames the gif

`!gif <shortcut>` - sends the gif to the channel as an embedded file

#### Birthday
`!birthday` - returns the next birthday in the chat

#### Stats Collection
`!stats <@person|#channel> <time>` - see how many messages were posted by @person OR in #channel in the past 24 hours, 1 week, 1 month, or all-time

`!more-stats <@person|#channel> <time>` - see the top 5 channels @person has posted in OR or the top 5 posters in #channel in `<time>`

`!most-stats <@person|#channel> <time>` - see all of the channels OR all of the posters in `<time>`

#### Unit Conversion
`!convert <number> <unit> [to <new unit>]` - converts temperature, length, and weight between imperial and metric

#### Bot Praising
`!pet` - returns a random affectionate message from the bot

## Other Features:

#### Auto-Pinning
Pins any message that gets reacted to with the 📌 emoji

#### Auto-Delete
Within the `#receipts` channel, deletes any message that gets reacted to with the 🗑 emoji

#### Link Collection
Crossposts any (non-image) links in `#general` to a read-only, link collection channel. It only reposts links to the channel once 24 hours have passed since it was last posted.

## In Progress:

None