from discord.ext.commands import Bot


def assert_cog_added_of_type(bot: Bot, cog_type):
    """Asserts a cog of the given type was added to the bot."""
    called = False
    for invocation in bot.add_cog.call_args_list:
        if isinstance(invocation[0][0], cog_type):
            called = True
    if not called:
        # this fails with a decent assertion failure message
        bot.add_cog.assert_any_call(cog_type)
