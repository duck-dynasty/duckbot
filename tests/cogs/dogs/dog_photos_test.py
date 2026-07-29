import pytest

from duckbot.cogs.dogs import DogPhotos
from tests.discord_test_ext import bind_commands

RANDOM_IMAGE_URI = "https://dog.ceo/api/breeds/image/random"
LIST_BREEDS_URI = "https://dog.ceo/api/breeds/list/all"


@pytest.fixture
def clazz() -> DogPhotos:
    return bind_commands(DogPhotos())


def test_get_dog_image_any_breed_success(clazz, responses):
    responses.add(responses.GET, RANDOM_IMAGE_URI, json=build_dog("dog", success=True))
    response = clazz.get_dog_image()
    assert response == "dog"
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == RANDOM_IMAGE_URI


@pytest.mark.parametrize("breed,path", [("collie", "collie"), ("border collie", "collie/border"), ("dog", "dog")])
def test_get_dog_image_given_breed_success(clazz, responses, breed, path):
    responses.add(responses.GET, f"https://dog.ceo/api/breed/{path}/images/random", json=build_dog(f"{breed} result", success=True))
    response = clazz.get_dog_image(breed)
    assert response == f"{breed} result"
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == f"https://dog.ceo/api/breed/{path}/images/random"


def test_get_dog_image_failure(clazz, responses):
    responses.add(responses.GET, RANDOM_IMAGE_URI, json=build_dog("dog", success=False))
    with pytest.raises(RuntimeError):
        clazz.get_dog_image()
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == RANDOM_IMAGE_URI


def test_get_dog_image_no_message(clazz, responses):
    responses.add(responses.GET, RANDOM_IMAGE_URI, json=build_dog("", success=True))
    with pytest.raises(RuntimeError):
        clazz.get_dog_image()
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == RANDOM_IMAGE_URI


def test_get_breeds_success(clazz, responses):
    responses.add(responses.GET, LIST_BREEDS_URI, json=build_breeds(success=True))
    response = clazz.get_breeds()
    assert response == ["collie", "border collie", "dog"]
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == LIST_BREEDS_URI


def test_get_breeds_failure(clazz, responses):
    responses.add(responses.GET, LIST_BREEDS_URI, json=build_breeds(success=False))
    with pytest.raises(RuntimeError):
        clazz.get_breeds()
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == LIST_BREEDS_URI


async def test_dog_no_breed(clazz, context, responses):
    responses.add(responses.GET, RANDOM_IMAGE_URI, json=build_dog("result", success=True))
    await clazz.dog(context, breed=None)
    context.send.assert_called_once_with("result")
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == RANDOM_IMAGE_URI


async def test_dog_known_breed(clazz, context, responses):
    responses.add(responses.GET, LIST_BREEDS_URI, json=build_breeds(success=True))
    responses.add(responses.GET, "https://dog.ceo/api/breed/collie/images/random", json=build_dog("pup", success=True))
    await clazz.dog(context, breed="collie")
    context.send.assert_called_once_with("pup")
    assert len(responses.calls) == 2
    assert responses.calls[0].request.url == LIST_BREEDS_URI
    assert responses.calls[1].request.url == "https://dog.ceo/api/breed/collie/images/random"


async def test_dog_unknown_breed(clazz, context, responses):
    responses.add(responses.GET, LIST_BREEDS_URI, json=build_breeds(success=True))
    responses.add(responses.GET, RANDOM_IMAGE_URI, json=build_dog("flup", success=True))
    await clazz.dog(context, breed="who?")
    context.send.assert_called_once_with("flup")
    assert len(responses.calls) == 2
    assert responses.calls[0].request.url == LIST_BREEDS_URI
    assert responses.calls[1].request.url == RANDOM_IMAGE_URI


async def test_breed_autocomplete_narrows_to_matches(clazz, responses):
    responses.add(responses.GET, LIST_BREEDS_URI, json=build_breeds(success=True))
    result = await clazz.breed_autocomplete(None, "col")
    assert [c.value for c in result] == ["collie", "border collie"]


async def test_breed_autocomplete_no_input_returns_everything(clazz, responses):
    responses.add(responses.GET, LIST_BREEDS_URI, json=build_breeds(success=True))
    result = await clazz.breed_autocomplete(None, "")
    assert [c.value for c in result] == ["collie", "border collie", "dog"]


async def test_breed_autocomplete_fetches_breeds_once(clazz, responses):
    responses.add(responses.GET, LIST_BREEDS_URI, json=build_breeds(success=True))
    await clazz.breed_autocomplete(None, "c")
    await clazz.breed_autocomplete(None, "co")
    assert len(responses.calls) == 1


def build_dog(img, success):
    return {"message": img, "status": "success" if success else "failure"}


def build_breeds(success):
    return {"message": {"collie": ["border"], "dog": []}, "status": "success" if success else "failure"}
