from abc import ABC, abstractmethod

import moviepy as mp
from sqlalchemy.future import select

from ..chore import GenerationContext
from ..models import SessionLocal, File, Setting


class BaseEngine(ABC):
    num_options: int
    name: str
    description: str

    def __init__(self):
        self.ctx: GenerationContext  # This is for type hinting only

    @classmethod
    @abstractmethod
    def get_options(cls):
        ...

    def get_video_duration(self, path: str) -> float:
        return mp.VideoFileClip(path).duration

    def get_audio_duration(self, path: str) -> float:
        return mp.AudioFileClip(path).duration

    # noinspection PyShadowingBuiltins
    @classmethod
    def get_assets(cls, *, type: str = None, by_id: int = None) -> list[File] | File | None:
        with SessionLocal() as db:
            if type:
                # noinspection PyTypeChecker
                return (
                    db.execute(
                        select(File).filter(
                            File.type == type, File.provider == cls.name
                        )
                    )
                    .scalars()
                    .all()
                )
            elif by_id:
                # noinspection PyTypeChecker
                return (
                    db.execute(
                        select(File).filter(
                            File.id == by_id, File.provider == cls.name
                        )
                    )
                    .scalars()
                    .first()
                )
            else:
                # noinspection PyTypeChecker
                return (
                    db.execute(select(File).filter(File.provider == cls.name))
                    .scalars()
                    .all()
                )

    # noinspection PyShadowingBuiltins
    @classmethod
    def add_asset(cls, *, path: str, metadata: dict, type: str = None):
        with SessionLocal() as db:
            db.add(File(path=path, data=metadata, type=type, provider=cls.name))
            db.commit()

    @classmethod
    def remove_asset(cls, *, path: str):
        with SessionLocal() as db:
            # noinspection PyTypeChecker
            db.execute(select(File).filter(File.path == path)).delete()
            db.commit()

    # noinspection PyShadowingBuiltins
    @classmethod
    def store_setting(cls, *, identifier: str = None, type: str = None, data: dict):
        if not identifier and type:
            identifier = type
        with SessionLocal() as db:
            # check if setting exists
            # noinspection PyTypeChecker
            setting = db.execute(
                select(Setting).filter(
                    Setting.provider == cls.name, Setting.type == identifier
                )
            ).scalar()
            if setting:
                setting.data = data
            else:
                db.add(Setting(provider=cls.name, type=identifier, data=data))
            db.commit()

    @classmethod
    def get_setting(cls, *args, **kwargs):
        """
        This method is deprecated, use retrieve_setting instead
        """
        return cls.retrieve_setting(*args, **kwargs)

    # noinspection PyShadowingBuiltins
    @classmethod
    def retrieve_setting(cls, *, identifier: str = None, type: str = None) -> dict | list[dict] | None:
        """
        Retrieve a setting from the database based on the provided identifier or type.

        Args:
            identifier (str, optional): The identifier of the setting. Defaults to None.
            type (str, optional): Deprecated. Now an alias for identifier, please use identifier instead. Defaults to None.

        Returns:
            str | list[str] | None: The retrieved setting data, or None if not found.
        """
        with SessionLocal() as db:
            if not identifier and type:
                identifier = type
            if identifier:
                # noinspection PyTypeChecker
                result = db.execute(
                    select(Setting).filter(
                        Setting.provider == cls.name, Setting.type == identifier
                    )
                ).scalar()

                if result:
                    return result.data
                return None
            else:
                # noinspection PyTypeChecker
                return [
                    s.data
                    for s in db.execute(
                        select(Setting).filter(Setting.provider == cls.name)
                    )
                    .scalars()
                    .all()
                ]

    # noinspection PyShadowingBuiltins
    @classmethod
    def remove_setting(cls, *, identifier: str = None, type: str = None):
        """
        Remove a setting from the database.

        Args:
            identifier (str, optional): The identifier of the setting to be removed. If not provided, the type will be used as the identifier. Defaults to None.
            type (str, optional): Deprecated. Now an alias for identifier, please use identifier instead. Defaults to None.
        """
        with SessionLocal() as db:
            if not identifier and type:
                identifier = type
            if identifier:
                # noinspection PyTypeChecker
                db.execute(
                    select(Setting).filter(
                        Setting.provider == cls.name, Setting.type == identifier
                    )
                ).delete()
            else:
                # noinspection PyTypeChecker
                db.execute(
                    select(Setting).filter(Setting.provider == cls.name)
                ).delete()
            db.commit()

    @classmethod
    def get_settings(cls):
        ...
