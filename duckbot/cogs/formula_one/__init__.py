from .formula_one import FormulaOne


def setup(bot):
    bot.add_cog(FormulaOne(bot))
