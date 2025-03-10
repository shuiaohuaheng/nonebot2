import pytest
from nonebug import App

from utils import make_fake_event, make_fake_message


@pytest.mark.asyncio
async def test_depend(app: App, load_plugin):
    from nonebot.params import DependParam
    from plugins.param.param_depend import (
        ClassDependency,
        runned,
        depends,
        class_depend,
        test_depends,
    )

    async with app.test_dependent(depends, allow_types=[DependParam]) as ctx:
        ctx.should_return(1)

    assert len(runned) == 1 and runned[0] == 1

    runned.clear()

    async with app.test_matcher(test_depends) as ctx:
        bot = ctx.create_bot()
        event_next = make_fake_event()()
        ctx.receive_event(bot, event_next)

    assert len(runned) == 2 and runned[0] == runned[1] == 1

    async with app.test_dependent(class_depend, allow_types=[DependParam]) as ctx:
        ctx.should_return(ClassDependency(x=1, y=2))


@pytest.mark.asyncio
async def test_bot(app: App, load_plugin):
    from nonebot.params import BotParam
    from nonebot.exception import TypeMisMatch
    from plugins.param.param_bot import (
        FooBot,
        get_bot,
        not_bot,
        sub_bot,
        union_bot,
        legacy_bot,
        not_legacy_bot,
    )

    async with app.test_dependent(get_bot, allow_types=[BotParam]) as ctx:
        bot = ctx.create_bot()
        ctx.pass_params(bot=bot)
        ctx.should_return(bot)

    async with app.test_dependent(legacy_bot, allow_types=[BotParam]) as ctx:
        bot = ctx.create_bot()
        ctx.pass_params(bot=bot)
        ctx.should_return(bot)

    with pytest.raises(ValueError):
        async with app.test_dependent(not_legacy_bot, allow_types=[BotParam]) as ctx:
            ...

    async with app.test_dependent(sub_bot, allow_types=[BotParam]) as ctx:
        bot = ctx.create_bot(base=FooBot)
        ctx.pass_params(bot=bot)
        ctx.should_return(bot)

    with pytest.raises(TypeMisMatch):
        async with app.test_dependent(sub_bot, allow_types=[BotParam]) as ctx:
            bot = ctx.create_bot()
            ctx.pass_params(bot=bot)

    async with app.test_dependent(union_bot, allow_types=[BotParam]) as ctx:
        bot = ctx.create_bot(base=FooBot)
        ctx.pass_params(bot=bot)
        ctx.should_return(bot)

    with pytest.raises(ValueError):
        async with app.test_dependent(not_bot, allow_types=[BotParam]) as ctx:
            ...


@pytest.mark.asyncio
async def test_event(app: App, load_plugin):
    from nonebot.exception import TypeMisMatch
    from nonebot.params import EventParam, DependParam
    from plugins.param.param_event import (
        FooEvent,
        event,
        not_event,
        sub_event,
        event_type,
        event_to_me,
        union_event,
        legacy_event,
        event_message,
        event_plain_text,
        not_legacy_event,
    )

    fake_message = make_fake_message()("text")
    fake_event = make_fake_event(_message=fake_message)()
    fake_fooevent = make_fake_event(_base=FooEvent)()

    async with app.test_dependent(event, allow_types=[EventParam]) as ctx:
        ctx.pass_params(event=fake_event)
        ctx.should_return(fake_event)

    async with app.test_dependent(legacy_event, allow_types=[EventParam]) as ctx:
        ctx.pass_params(event=fake_event)
        ctx.should_return(fake_event)

    with pytest.raises(ValueError):
        async with app.test_dependent(
            not_legacy_event, allow_types=[EventParam]
        ) as ctx:
            ...

    async with app.test_dependent(sub_event, allow_types=[EventParam]) as ctx:
        ctx.pass_params(event=fake_fooevent)
        ctx.should_return(fake_fooevent)

    with pytest.raises(TypeMisMatch):
        async with app.test_dependent(sub_event, allow_types=[EventParam]) as ctx:
            ctx.pass_params(event=fake_event)

    async with app.test_dependent(union_event, allow_types=[EventParam]) as ctx:
        ctx.pass_params(event=fake_fooevent)
        ctx.should_return(fake_event)

    with pytest.raises(ValueError):
        async with app.test_dependent(not_event, allow_types=[EventParam]) as ctx:
            ...

    async with app.test_dependent(
        event_type, allow_types=[EventParam, DependParam]
    ) as ctx:
        ctx.pass_params(event=fake_event)
        ctx.should_return(fake_event.get_type())

    async with app.test_dependent(
        event_message, allow_types=[EventParam, DependParam]
    ) as ctx:
        ctx.pass_params(event=fake_event)
        ctx.should_return(fake_event.get_message())

    async with app.test_dependent(
        event_plain_text, allow_types=[EventParam, DependParam]
    ) as ctx:
        ctx.pass_params(event=fake_event)
        ctx.should_return(fake_event.get_plaintext())

    async with app.test_dependent(
        event_to_me, allow_types=[EventParam, DependParam]
    ) as ctx:
        ctx.pass_params(event=fake_event)
        ctx.should_return(fake_event.is_tome())


@pytest.mark.asyncio
async def test_state(app: App, load_plugin):
    from nonebot.params import StateParam, DependParam
    from nonebot.consts import (
        CMD_KEY,
        REGEX_STR,
        PREFIX_KEY,
        REGEX_DICT,
        SHELL_ARGS,
        SHELL_ARGV,
        CMD_ARG_KEY,
        KEYWORD_KEY,
        RAW_CMD_KEY,
        REGEX_GROUP,
        ENDSWITH_KEY,
        CMD_START_KEY,
        FULLMATCH_KEY,
        REGEX_MATCHED,
        STARTSWITH_KEY,
    )
    from plugins.param.param_state import (
        state,
        command,
        keyword,
        endswith,
        fullmatch,
        regex_str,
        regex_dict,
        startswith,
        command_arg,
        raw_command,
        regex_group,
        legacy_state,
        command_start,
        regex_matched,
        not_legacy_state,
        shell_command_args,
        shell_command_argv,
    )

    fake_message = make_fake_message()("text")
    fake_state = {
        PREFIX_KEY: {
            CMD_KEY: ("cmd",),
            RAW_CMD_KEY: "/cmd",
            CMD_START_KEY: "/",
            CMD_ARG_KEY: fake_message,
        },
        SHELL_ARGV: ["-h"],
        SHELL_ARGS: {"help": True},
        REGEX_MATCHED: "[cq:test,arg=value]",
        REGEX_STR: "[cq:test,arg=value]",
        REGEX_GROUP: ("test", "arg=value"),
        REGEX_DICT: {"type": "test", "arg": "value"},
        STARTSWITH_KEY: "startswith",
        ENDSWITH_KEY: "endswith",
        FULLMATCH_KEY: "fullmatch",
        KEYWORD_KEY: "keyword",
    }

    async with app.test_dependent(state, allow_types=[StateParam]) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state)

    async with app.test_dependent(legacy_state, allow_types=[StateParam]) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state)

    with pytest.raises(ValueError):
        async with app.test_dependent(
            not_legacy_state, allow_types=[StateParam]
        ) as ctx:
            ...

    async with app.test_dependent(
        command, allow_types=[StateParam, DependParam]
    ) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state[PREFIX_KEY][CMD_KEY])

    async with app.test_dependent(
        raw_command, allow_types=[StateParam, DependParam]
    ) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state[PREFIX_KEY][RAW_CMD_KEY])

    async with app.test_dependent(
        command_arg, allow_types=[StateParam, DependParam]
    ) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state[PREFIX_KEY][CMD_ARG_KEY])

    async with app.test_dependent(
        command_start, allow_types=[StateParam, DependParam]
    ) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state[PREFIX_KEY][CMD_START_KEY])

    async with app.test_dependent(
        shell_command_argv, allow_types=[StateParam, DependParam]
    ) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state[SHELL_ARGV])

    async with app.test_dependent(
        shell_command_args, allow_types=[StateParam, DependParam]
    ) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state[SHELL_ARGS])

    async with app.test_dependent(
        regex_matched, allow_types=[StateParam, DependParam]
    ) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state[REGEX_MATCHED])

    async with app.test_dependent(
        regex_str, allow_types=[StateParam, DependParam]
    ) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state[REGEX_STR])

    async with app.test_dependent(
        regex_group, allow_types=[StateParam, DependParam]
    ) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state[REGEX_GROUP])

    async with app.test_dependent(
        regex_dict, allow_types=[StateParam, DependParam]
    ) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state[REGEX_DICT])

    async with app.test_dependent(
        startswith, allow_types=[StateParam, DependParam]
    ) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state[STARTSWITH_KEY])

    async with app.test_dependent(
        endswith, allow_types=[StateParam, DependParam]
    ) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state[ENDSWITH_KEY])

    async with app.test_dependent(
        fullmatch, allow_types=[StateParam, DependParam]
    ) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state[FULLMATCH_KEY])

    async with app.test_dependent(
        keyword, allow_types=[StateParam, DependParam]
    ) as ctx:
        ctx.pass_params(state=fake_state)
        ctx.should_return(fake_state[KEYWORD_KEY])


@pytest.mark.asyncio
async def test_matcher(app: App, load_plugin):
    from nonebot.matcher import Matcher
    from nonebot.params import DependParam, MatcherParam
    from plugins.param.param_matcher import matcher, receive, last_receive

    fake_matcher = Matcher()

    async with app.test_dependent(matcher, allow_types=[MatcherParam]) as ctx:
        ctx.pass_params(matcher=fake_matcher)
        ctx.should_return(fake_matcher)

    event = make_fake_event()()
    fake_matcher.set_receive("test", event)
    event_next = make_fake_event()()
    fake_matcher.set_receive("", event_next)

    async with app.test_dependent(
        receive, allow_types=[MatcherParam, DependParam]
    ) as ctx:
        ctx.pass_params(matcher=fake_matcher)
        ctx.should_return(event)

    async with app.test_dependent(
        last_receive, allow_types=[MatcherParam, DependParam]
    ) as ctx:
        ctx.pass_params(matcher=fake_matcher)
        ctx.should_return(event_next)


@pytest.mark.asyncio
async def test_arg(app: App, load_plugin):
    from nonebot.matcher import Matcher
    from nonebot.params import ArgParam
    from plugins.param.param_arg import arg, arg_str, arg_plain_text

    matcher = Matcher()
    message = make_fake_message()("text")
    matcher.set_arg("key", message)

    async with app.test_dependent(arg, allow_types=[ArgParam]) as ctx:
        ctx.pass_params(matcher=matcher)
        ctx.should_return(message)

    async with app.test_dependent(arg_str, allow_types=[ArgParam]) as ctx:
        ctx.pass_params(matcher=matcher)
        ctx.should_return(str(message))

    async with app.test_dependent(arg_plain_text, allow_types=[ArgParam]) as ctx:
        ctx.pass_params(matcher=matcher)
        ctx.should_return(message.extract_plain_text())


@pytest.mark.asyncio
async def test_exception(app: App, load_plugin):
    from nonebot.params import ExceptionParam
    from plugins.param.param_exception import exc

    exception = ValueError("test")
    async with app.test_dependent(exc, allow_types=[ExceptionParam]) as ctx:
        ctx.pass_params(exception=exception)
        ctx.should_return(exception)


@pytest.mark.asyncio
async def test_default(app: App, load_plugin):
    from nonebot.params import DefaultParam
    from plugins.param.param_default import default

    async with app.test_dependent(default, allow_types=[DefaultParam]) as ctx:
        ctx.should_return(1)
