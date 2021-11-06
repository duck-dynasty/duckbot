import logging
from typing import List, Optional

from discord import Client, Embed, File, Guild, Interaction, Message, VoiceProtocol
from discord.ext.commands import Command
from discord.ext.commands.view import StringView

log = logging.getLogger(__name__)


def _create_arguments_view(interaction: Interaction, command: Command) -> StringView:
    # create option string by joining all of the arguments together, so we can delegate to discord.py
    # note that slash commands can accept spaces in their args, whereas discord.py required "bash style quotes"
    options = interaction.data.get("options", [])
    parts = []
    if options and not options[0].get("value", None):  # a command group
        if command._discordpy_include_subcommand_name[options[0]["name"]]:
            parts.append(options[0]["name"])
        parts = parts + [f'"{x.get("value", "")}"' for x in options[0].get("options", [])]
    else:
        parts = parts + [f'"{x.get("value", "")}"' for x in options]
    view = " ".join([x for x in parts])
    log.debug("args string=%s", view)
    return StringView(view)


class InteractionContext:
    """A slash duplication of `discord.ext.commands.Context`, meant to bridge between
    discord.py commands and discord slash commands.

    This class will have mostly the same interface as `Context`, but will call interaction
    based discord APIs instead of traditional message based ones.
    Fair word of warning, it is substantially trimmed down. Missing features from `Context`
    will be added on an as-needed basis."""

    def __init__(self, *, bot: Client, interaction: Interaction, command: Command):
        self.bot = bot
        self._interaction = interaction
        self._command = command
        self.invoked_with = None
        self.invoked_parents = []
        self.invoked_subcommand = None
        self.subcommand_passed = None
        self.command_failed = False
        self.view = _create_arguments_view(interaction, command)
        self.follow_up = False

    @property
    def interaction(self) -> Interaction:
        return self._interaction

    @property
    def channel(self):
        return self.interaction.channel

    @property
    def guild(self) -> Optional[Guild]:
        return self.interaction.guild

    @property
    def voice_client(self) -> Optional[VoiceProtocol]:
        return self.guild.voice_client if self.guild else None

    @property
    def message(self) -> Optional[Message]:
        return self.interaction.message  # discord.py context ALWAYS has a message, this is an interface mismatch

    @property
    def author(self):
        return self.interaction.user

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        self._command = value

    async def send(self, content="", *, embed: Optional[Embed] = None, embeds: Optional[List[Embed]] = None, file: Optional[File] = None, delete_after: Optional[float] = None) -> None:
        """Send a message as a response to an interaction. There are some restrictions to this, see `typing()`.

        :param content: the message content to send
        :param embed: embed message content to send, mutually exclusive with embeds
        :param embeds: multiple embed message contents to send, mutually exclusive with embed
        :param file: a file to upload and sent; requires `typing()` first
        :param delete_after: does nothing, exists for interface parity with discord.py
        :return: None
        """
        if self.follow_up:
            kwargs = {"embed": embed, "embeds": embeds, "file": file}
            await self.interaction.followup.send(content, **{k: v for k, v in kwargs.items() if v})
        else:
            kwargs = {"embed": embed, "embeds": embeds}
            await self.interaction.response.send_message(content, **{k: v for k, v in kwargs.items() if v})

    def typing(self):
        """Triggers a "Bot is thinking..." response to the interaction. Should be used in any of the following conditions:
        1. The command is unable to response within three seconds. The interaction token lifespan is increased to 15 minutes
        after calling `typing()`.
        2. The response will contain a file. Discord.py for whatever reason only allows files to be sent via webhooks, which
        is what messages turn into after `typing()` is called.
        3. Multiple responses will be sent. All of the `send()` calls should be wrapped in `typing()`."""
        return self

    async def __aenter__(self):
        await self.interaction.response.defer()
        self.follow_up = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None
