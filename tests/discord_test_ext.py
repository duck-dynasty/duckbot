from discord.ext.commands import Bot


def assert_cog_added_of_type(bot: Bot, tpye):
    """Asserts a cog of the given type was added to the bot."""
    called = False
    for invocation in bot.add_cog.call_args_list:
        if isinstance(invocation[0][0], tpye):
            called = True
    if not called:
        bot.add_cog.assert_any_call(tpye)
