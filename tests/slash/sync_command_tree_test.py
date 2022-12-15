from duckbot.slash import SyncCommandTree


async def test_sync_command_tree_prod_creates_global_only(bot, tree, guild, app_config):
    app_config.is_production = True
    bot.tree = tree
    bot.guilds = [guild]
    clazz = SyncCommandTree(bot)
    await clazz.sync_command_tree()
    tree.sync.assert_called_once()


async def test_sync_command_tree_not_prod_creates_in_guild(bot, tree, guild, app_config):
    app_config.is_production = False
    bot.tree = tree
    bot.guilds = [guild]
    clazz = SyncCommandTree(bot)
    await clazz.sync_command_tree()
    tree.sync.assert_called()
    tree.sync.assert_called_with(guild=guild)
