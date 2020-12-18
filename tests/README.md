# Test Gotchas
`pytest` kinda sucks. Here's the list of things we've had issues with
and how to deal with it.

## @commands.command
For some reason, including `self` as a parameter to a command method
breaks in tests. Without `self`, the bot itself fails.  
In order to test a `@command` method, delegate all the work to a new
method and have the `@command` method do nothing else.

```python
# src
class MyClass(commands.Cog):
    @command(name = "bar")
    async def foo(self, context):
        await self.__foo(context)
    async def __foo(self, context)
        print("I FOO")

# test
async def test_foo(bot, context_mock):
    clazz = Foo(bot)
    await clazz._MyClass__foo(context_mock)
    # ... assertions ...
```
