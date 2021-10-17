from unittest import mock

import pytest

from duckbot.cogs.dogs import DogPhotos
from tests.duckmock.urllib import patch_urlopen

RANDOM_IMAGE_URI = "https://dog.ceo/api/breeds/image/random"
LIST_BREEDS_URI = "https://dog.ceo/api/breeds/list/all"


def build_dog(img, success):
    return {"message": img, "status": "success" if success else "failure"}


def build_breeds(success):
    return {"message": {"collie": ["border"], "dog": []}, "status": "success" if success else "failure"}


def test_get_dog_image_any_breed_success(bot, responses):
    responses.add(responses.GET, RANDOM_IMAGE_URI, json=build_dog("dog", True))
    clazz = DogPhotos(bot)
    response = clazz.get_dog_image()
    assert response == "dog"
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == RANDOM_IMAGE_URI


@pytest.mark.parametrize("breed,path", [("collie", "collie"), ("border collie", "collie/border"), ("dog", "dog")])
def test_get_dog_image_given_breed_success(bot, responses, breed, path):
    responses.add(responses.GET, f"https://dog.ceo/api/breed/{path}/images/random", json=build_dog(f"{breed} result", True))
    clazz = DogPhotos(bot)
    response = clazz.get_dog_image(breed)
    assert response == f"{breed} result"
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == f"https://dog.ceo/api/breed/{path}/images/random"


def test_get_dog_image_failure(bot, responses):
    responses.add(responses.GET, RANDOM_IMAGE_URI, json=build_dog("dog", False))
    clazz = DogPhotos(bot)
    with pytest.raises(RuntimeError):
        clazz.get_dog_image()
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == RANDOM_IMAGE_URI


def test_get_dog_image_no_message(bot, responses):
    responses.add(responses.GET, RANDOM_IMAGE_URI, json=build_dog("", True))
    clazz = DogPhotos(bot)
    with pytest.raises(RuntimeError):
        clazz.get_dog_image()
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == RANDOM_IMAGE_URI


@mock.patch("urllib.request.Request")
def get_breeds_success(req, bot):
    with patch_urlopen(build_breeds(True)):
        clazz = DogPhotos(bot)
        response = clazz.get_breeds()
        assert response == ["collie", "border collie", "dog"]
        req.assert_any_call(LIST_BREEDS_URI)


@mock.patch("urllib.request.Request")
def get_breeds_failure(req, bot):
    with patch_urlopen(build_breeds(False)):
        clazz = DogPhotos(bot)
        with pytest.raises(RuntimeError):
            clazz.get_breeds()
        req.assert_any_call(LIST_BREEDS_URI)


@pytest.mark.asyncio
@mock.patch("urllib.request.Request")
async def dog_no_breed(req, bot, context):
    with patch_urlopen(build_dog("result", True)):
        clazz = DogPhotos(bot)
        await clazz.dog(context, None)
        context.send.assert_called_once_with("result")
        req.assert_called_once_with(RANDOM_IMAGE_URI)


@pytest.mark.asyncio
@mock.patch("urllib.request.Request")
async def dog_known_breed(req, bot, context):
    with patch_urlopen([build_breeds(True), build_dog("pup", True)]):
        clazz = DogPhotos(bot)
        await clazz.dog(context, "collie")
        context.send.assert_called_once_with("pup")
        req.assert_any_call(LIST_BREEDS_URI)
        req.assert_any_call("https://dog.ceo/api/breed/collie/images/random")


@pytest.mark.asyncio
@mock.patch("urllib.request.Request")
async def dog_unknown_breed(req, bot, context):
    with patch_urlopen([build_breeds(True), build_dog("flup", True)]):
        clazz = DogPhotos(bot)
        await clazz.dog(context, "who?")
        context.send.assert_called_once_with("flup")
        req.assert_any_call(LIST_BREEDS_URI)
        req.assert_any_call(RANDOM_IMAGE_URI)
