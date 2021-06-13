* [Message Responses](#message-responses)
* [Scheduled Tasks](#scheduled-tasks)

Message Responses
=================

Message Edits
-------------
If you edit a message, DuckBot will give you a helpful diff of the changes.

> Human: I hate you.

Say that's edited to:

> Human: I don't hate you.

Then DuckBot will respond with the following message (it is deleted after a short period).
> DuckBot: :eyes: @Human  
> I {+don't +}hate you.

Haiku
-----
DuckBot will let you know if a message is a 5/7/5 haiku.

Bitcoin
-------
DuckBot kindly corrects the spelling of _bitcoin_ to _magic beans_.

Kubernetes
----------
DuckBot kindly corrects the spelling of _k8s_ to _kubernetes_. Additionally, DuckBot corrects the spelling of _kubernetes_ to _k8s_.

Formula One
-----------
DuckBot gets HYPED UP over posts to the F1 related `#dank` channel, so it reacts to every single message there.

Age of Empires
--------------
DuckBot will replace any [Age of Empires II taunts](https://ageofempires.fandom.com/wiki/Taunts#Full_list_of_taunts) with their text expansion. For example,

> Human: 2  
> DuckBot: @Human > 2: No.

Josip Broz Tito
---------------
Heeeyyyy Mr. Tito! DuckBot will react to messages containing the custom `:tito:` emoji with all the country flags of the formally Yugoslavian countries. DuckBot will do the same when someone reacts with `:tito:`.

Typo Correction
---------------
DuckBot will attempt to correct typos a user's previous message when they send _fuck_. For example,

> Human: I wanted to eat teh duck wiht thier creamy sauce.  
> Human: fuck  
> DuckBot:
>    > I wanted to eat the duck with their creamy sauce.
>
> There, I fixed it for you, @Human!

DuckBoard
-----
DuckBot has a very small chance to react to any message with 🦆 .

Robot
-----
DuckBot is a robot, and as such does not like being humanized. DuckBot tells people to stop thanking a robot when they explicitly thank the robot.


Scheduled Tasks
===============

Day Announcements
-----------------
Every day in the 7am hour, DuckBot will announce to the general channel the current day of the week. If the day is also a statutory holiday, or an otherwise special day, DuckBot will announce that at the same time. You can run this on demand using the `!day` command.
