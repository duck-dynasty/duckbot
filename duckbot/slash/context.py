import json
from typing import Optional

import aiohttp
import discord
from discord import Client
from discord.ext.commands import Command
from discord.ext.commands.view import StringView

from .interaction import Interaction
from .route import Route8


class InteractionContext:
    r"""A slash duplication of `discord.ext.commands.Context`, meant to bridge between
    discord-py commands and discord slash commands.

    This class will have mostly the same interface as `Context`, but will call interaction
    based discord APIs instead of traditional message based ones.
    Fair word of warning, it is substantially trimmed down. Missing features from `Context`
    will be added on an as-needed basis.
    """

    def __init__(self, *, bot: Client, interaction: Interaction, command: Command):
        self.bot = bot
        self._interaction = interaction
        self._command = command
        self.invoked_with = None
        self.invoked_parents = []
        self.invoked_subcommand = None
        self.subcommand_passed = None
        self.command_failed = False
        self._state = bot._connection
        options = interaction.data.get("options", [])
        # create option string by joining all of the arguments together, so we can delegate to discord-py
        # NOTE slash commands can accept spaces in their args, whereas discord-py required "bash style quotes"
        # we have no use for spaces in args yet, but this would be the place to fix once we do
        if options and options[0] and not options[0].get("value", None):
            if command._slash_discordpy_adapt_name[options[0]["name"]]:
                self.view = options[0]["name"] + " " + " ".join([x.get("value", "") for x in options[0].get("options", [])])
            else:
                self.view = " ".join([x.get("value", "") for x in options[0].get("options", [])])
        else:
            self.view = " ".join([x.get("value", "") for x in options])
        self.view = StringView(self.view)
        self.follow_up = False

    @property
    def interaction(self) -> Interaction:
        return self._interaction

    @property
    def channel(self):
        return self.interaction.channel

    @property
    def guild(self):
        return self.interaction.guild

    @property
    def author(self):
        return self.interaction.author

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        self._command = value

    async def send(self, content="", *, embed: Optional[discord.Embed] = None, file: Optional[discord.File] = None, delete_after: Optional[float] = None) -> None:
        """
        Send a message as a response to an interaction.
        If you want to send multiple responses, you have to use `typing()` first.

        :param content: the message content to send
        :param embed: embed message content to send
        :param file: a file to upload and sent
        :param delete_after: does nothing, exists for interface parity with discordpy
        :return: None
        """
        if self.follow_up:
            json_payload = {"content": content, "embeds": [embed.to_dict()] if embed else [], "tts": False}
            route = Route8("POST", f"/webhooks/{self.interaction.application_id}/{self.interaction.token}")
        else:
            json_payload = {"type": 4, "data": {"content": content, "embeds": [embed.to_dict()] if embed else [], "tts": False}}
            route = Route8("POST", f"/interactions/{self.interaction.id}/{self.interaction.token}/callback")
        if file:
            form = aiohttp.FormData()
            form.add_field("payload_json", json.dumps(json_payload))
            form.add_field("file", file.fp, filename=file.filename, content_type="application/octet-stream")
            await self.bot.http.request(route, data=form, files=[file])
        else:
            await self.bot.http.request(route, json=json_payload)

    def typing(self):
        """Triggers a "Bot is thinking..." response to the interaction.
        Discord requires a response to an interaction within three seconds. If your command requires more than three seconds,
        it is best to wrap it in `typing()` first, which will give you up the 15min to respond.

        Further, if you want to send multiple messages, you have to wrap all of them in `typing()` as well."""
        return self

    async def __aenter__(self):
        assert not self.follow_up
        json = {"type": 5, "data": {"content": ":thinking:"}}
        route = Route8("POST", f"/interactions/{self.interaction.id}/{self.interaction.token}/callback")
        await self.bot.http.request(route, json=json)
        self.follow_up = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None