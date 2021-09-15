# Test Thingamajigs

## Fixtures
We make heavy use of [pytest fixtures](https://docs.pytest.org/en/6.2.x/fixture.html) in order to test several use cases for many methods. See [the fixtures module](fixtures) for the list of global features available.

For example, whenever you use the `message` fixture, you'll produce several tests (or something! this readme may be out of date!). One for the message in a guild channel, one for a direct message and one for a group channel. The differences between the three are minor, but some fields may or may not be available. Like `member` is used in a guild channel, but `user` is used for direct messages. Voice clients may or may not be available, stuff like that. You can write your test once, and get three tests out of it pretty cheaply.

## @commands.command, @tasks.loop
In order to test a `@command` or `@loop` method, delegate all the work to a new method and have the `@method` method do nothing else. The decorators change the method signature, which makes the method itself too hard to test directly.

```python
# src
class Foo(commands.Cog):
    @command(name="foo")
    async def foo_command(self, context):
        await self.bar(context)
    async def foo(self, context):
        print("I FOO")

# test
async def test_foo(bot, context):
    clazz = Foo(bot)
    await clazz.foo(context)
    # ... assertions ...
```

Alternatively, you can make the delegate method private if you wish.

```python
# src
class Foo(commands.Cog):
    @command(name="foo")
    async def foo(self, context):
        await self.__foo(context)
    async def __foo(self, context):
        print("I FOO")

async def test_foo(bot, context):
    clazz = Foo(bot)
    await clazz._Foo__foo(context)
    # ... assertions ...
```
