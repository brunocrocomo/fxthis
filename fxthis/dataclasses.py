from typing import Optional, List
from pydantic.dataclasses import dataclass


@dataclass
class Attachments:
    media_keys: Optional[List[str]] = None


@dataclass
class Data:
    id: str
    text: str
    author_id: Optional[str] = None
    attachments: Optional[Attachments] = None


@dataclass
class User:
    id: Optional[str] = None
    name: Optional[str] = None
    username: Optional[str] = None


@dataclass
class Media:
    media_key: Optional[str] = None
    preview_image_url: Optional[str] = None
    type: Optional[str] = None


@dataclass
class Includes:
    users: Optional[List[User]] = None
    media: Optional[List[Media]] = None


@dataclass
class Tweet:
    data: Data
    includes: Includes
