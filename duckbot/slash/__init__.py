from .sync_command_tree import SyncCommandTree


async def setup(bot):
    await bot.add_cog(SyncCommandTree(bot))
