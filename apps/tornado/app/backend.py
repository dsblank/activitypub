import abc
import binascii
import os
import typing

import requests

from .__version__ import __version__
from .errors import ActivityNotFoundError
from .errors import RemoteActivityGoneError
from .urlutils import check_url as check_url

if typing.TYPE_CHECKING:
    from little_boxes import activitypub as ap  # noqa: type checking


class Backend(abc.ABC):
    def debug_mode(self) -> bool:
        """Should be overidded to return `True` in order to enable the debug mode."""
        return False

    def check_url(self, url: str) -> None:
        check_url(url, debug=self.debug_mode())

    def user_agent(self) -> str:
        return (
            f"{requests.utils.default_user_agent()} (Little Boxes/{__version__};"
            " +http://github.com/tsileo/little-boxes)"
        )

    def random_object_id(self) -> str:
        """Generates a random object ID."""
        return binascii.hexlify(os.urandom(8)).decode("utf-8")

    def fetch_json(self, url: str, **kwargs):
        self.check_url(url)
        resp = requests.get(
            url,
            headers={"User-Agent": self.user_agent(), "Accept": "application/json"},
            **kwargs,
        )

        resp.raise_for_status()

        return resp

    def is_from_outbox(
        self, as_actor: "ap.Person", activity: "ap.BaseActivity"
    ) -> bool:
        return activity.get_actor().id == as_actor.id

    @abc.abstractmethod
    def post_to_remote_inbox(
        self, as_actor: "ap.Person", payload_encoded: str, recp: str
    ) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def base_url(self) -> str:
        pass  # pragma: no cover

    def fetch_iri(self, iri: str, **kwargs) -> "ap.ObjectType":  # pragma: no cover
        self.check_url(iri)
        resp = requests.get(
            iri,
            headers={
                "User-Agent": self.user_agent(),
                "Accept": "application/activity+json",
            },
            **kwargs,
        )
        if resp.status_code == 404:
            raise ActivityNotFoundError(f"{iri} is not found")
        elif resp.status_code == 410:
            raise RemoteActivityGoneError(f"{iri} is gone")

        resp.raise_for_status()

        return resp.json()

    @abc.abstractmethod
    def inbox_check_duplicate(self, as_actor: "ap.Person", iri: str) -> bool:
        pass  # pragma: no cover

    @abc.abstractmethod
    def activity_url(self, obj_id: str) -> str:
        pass  # pragma: no cover

    @abc.abstractmethod
    def note_url(self, obj_id: str) -> str:
        pass  # pragma: no cover

    @abc.abstractmethod
    def outbox_create(self, as_actor: "ap.Person", activity: "ap.Create") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def outbox_delete(self, as_actor: "ap.Person", activity: "ap.Delete") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def inbox_create(self, as_actor: "ap.Person", activity: "ap.Create") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def inbox_delete(self, as_actor: "ap.Person", activity: "ap.Delete") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def outbox_is_blocked(self, as_actor: "ap.Person", actor_id: str) -> bool:
        pass  # pragma: no cover

    @abc.abstractmethod
    def inbox_new(self, as_actor: "ap.Person", activity: "ap.BaseActivity") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def outbox_new(self, as_actor: "ap.Person", activity: "ap.BaseActivity") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def new_follower(self, as_actor: "ap.Person", follow: "ap.Follow") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def new_following(self, as_actor: "ap.Person", follow: "ap.Follow") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def undo_new_follower(self, as_actor: "ap.Person", follow: "ap.Follow") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def undo_new_following(self, as_actor: "ap.Person", follow: "ap.Follow") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def inbox_update(self, as_actor: "ap.Person", activity: "ap.Update") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def outbox_update(self, as_actor: "ap.Person", activity: "ap.Update") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def inbox_like(self, as_actor: "ap.Person", activity: "ap.Like") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def inbox_undo_like(self, as_actor: "ap.Person", activity: "ap.Like") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def outbox_like(self, as_actor: "ap.Person", activity: "ap.Like") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def outbox_undo_like(self, as_actor: "ap.Person", activity: "ap.Like") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def inbox_announce(self, as_actor: "ap.Person", activity: "ap.Announce") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def inbox_undo_announce(
        self, as_actor: "ap.Person", activity: "ap.Announce"
    ) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def outbox_announce(self, as_actor: "ap.Person", activity: "ap.Announce") -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    def outbox_undo_announce(
        self, as_actor: "ap.Person", activity: "ap.Announce"
    ) -> None:
        pass  # pragma: no cover
