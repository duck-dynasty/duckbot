from .formula_one import FormulaOne


async def setup(bot):
    await bot.add_cog(FormulaOne(bot))
