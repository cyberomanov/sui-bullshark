from typing import List, Optional

from pydantic import BaseModel


class Name(BaseModel):
    title: str
    first: str
    last: str


class Street(BaseModel):
    number: int
    name: str


class Coordinates(BaseModel):
    latitude: str
    longitude: str


class Timezone(BaseModel):
    offset: str
    description: str


class Location(BaseModel):
    street: Street
    city: str
    state: str
    country: str
    postcode: int
    coordinates: Coordinates
    timezone: Timezone


class Login(BaseModel):
    uuid: str
    username: str
    password: str
    salt: str
    md5: str
    sha1: str
    sha256: str


class DOB(BaseModel):
    date: str
    age: int


class Registered(BaseModel):
    date: str
    age: int


class ID(BaseModel):
    name: str
    value: Optional[str]  # It can be None, so we use Optional


class Picture(BaseModel):
    large: str
    medium: str
    thumbnail: str


class Result(BaseModel):
    gender: str
    name: Name
    location: Location
    email: str
    login: Login
    dob: DOB
    registered: Registered
    phone: str
    cell: str
    id: ID
    picture: Picture
    nat: str


class Info(BaseModel):
    seed: str
    results: int
    page: int
    version: str


class NicknameResponse(BaseModel):
    results: List[Result]
    info: Info
