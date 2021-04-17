from discord.ext import commands
import signal


class Term(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.add_signal_handler(signal.SIGTERM)
        self.add_signal_handler(signal.SIGINT)
        self.add_signal_handler(signal.SIGKILL)
        self.add_signal_handler(signal.SIGSTOP)
        self.add_signal_handler(signal.SIGQUIT)
        self.add_signal_handler(signal.SIGTRAP)

    def add_signal_handler(self, signum):
        try:
            self.bot.loop.add_signal_handler(signum, self.kill_the_robots)
        except RuntimeError:
            print(signum)

    def kill_the_robots(self, signum, frame):
        print(f"{signum} received, icing the bot")
        self.bot.close()

