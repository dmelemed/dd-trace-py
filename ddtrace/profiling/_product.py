"""Product plugin that lets the profiler react to DEBUG remote config payloads."""

from collections.abc import Sequence
import typing as t

from ddtrace.internal.native import RemoteConfigProduct
from ddtrace.internal.remoteconfig import Payload
from ddtrace.internal.remoteconfig import RCCallback
from ddtrace.internal.settings.profiling import config as profiling_config


requires: list[str] = ["remote-configuration"]

# Config id to payload content, for every DEBUG config currently applied.
debug_configs: dict[str, dict[str, t.Any]] = {}


class DebugRCCallback(RCCallback):
    def __call__(self, payloads: Sequence[Payload]) -> None:
        for payload in payloads:
            if payload.metadata is None:
                continue
            if payload.content is None:
                debug_configs.pop(payload.metadata.id, None)
            else:
                debug_configs[payload.metadata.id] = payload.content
        print(f"[profiling] DEBUG RC configs: {debug_configs}")


def post_preload() -> None:
    pass


def enabled() -> bool:
    return profiling_config.enabled


def start() -> None:
    from ddtrace.internal.remoteconfig.worker import remoteconfig_poller

    remoteconfig_poller.register_callback(RemoteConfigProduct.Debug, DebugRCCallback())
    remoteconfig_poller.enable_product(RemoteConfigProduct.Debug)


def restart(join: bool = False) -> None:
    pass


def stop(join: bool = False) -> None:
    from ddtrace.internal.remoteconfig.worker import remoteconfig_poller

    remoteconfig_poller.unregister_callback(RemoteConfigProduct.Debug)
    remoteconfig_poller.disable_product(RemoteConfigProduct.Debug)
