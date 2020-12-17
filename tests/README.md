# Test Gotchas
`pytest` kinda sucks. Here's the list of things we've had issues with
and how to deal with it.

## @commands.command
Passing `self` as an argument to a command method breaks in tests.
The decorating function doesn't seem to pass `self` when you call the
method directly (the bot, presumably, invokes the command through different means).

In order to test a `@command` method, you've one of two options:

* If you don't need `self`, don't include it.
```python
# src
@command(name = "bar")
async def foo(context):
    print("I FOO")

# test
async def test_foo(bot, context_mock):
    clazz = Foo(bot)
    await clazz.foo(context_mock)
    # ... assertions ...
```

* If you need `self`, have your method delegate to another and do nothing else.
```python
# src
@command(name = "bar")
async def foo(self, context):
    await self.do_foo(context)

async def do_foo(self, context)
    print("I FOO")

# test
async def test_foo(bot, context_mock):
    clazz = Foo(bot)
    await clazz.do_foo(context_mock)
    # ... assertions ...
```
