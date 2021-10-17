import pytest

from duckbot.cogs.dogs import DogPhotos

RANDOM_IMAGE_URI = "https://dog.ceo/api/breeds/image/random"
LIST_BREEDS_URI = "https://dog.ceo/api/breeds/list/all"


def test_get_dog_image_any_breed_success(bot, responses):
    responses.add(responses.GET, RANDOM_IMAGE_URI, json=build_dog("dog", success=True))
    clazz = DogPhotos(bot)
    response = clazz.get_dog_image()
    assert response == "dog"
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == RANDOM_IMAGE_URI


@pytest.mark.parametrize("breed,path", [("collie", "collie"), ("border collie", "collie/border"), ("dog", "dog")])
def test_get_dog_image_given_breed_success(bot, responses, breed, path):
    responses.add(responses.GET, f"https://dog.ceo/api/breed/{path}/images/random", json=build_dog(f"{breed} result", success=True))
    clazz = DogPhotos(bot)
    response = clazz.get_dog_image(breed)
    assert response == f"{breed} result"
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == f"https://dog.ceo/api/breed/{path}/images/random"


def test_get_dog_image_failure(bot, responses):
    responses.add(responses.GET, RANDOM_IMAGE_URI, json=build_dog("dog", success=False))
    clazz = DogPhotos(bot)
    with pytest.raises(RuntimeError):
        clazz.get_dog_image()
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == RANDOM_IMAGE_URI


def test_get_dog_image_no_message(bot, responses):
    responses.add(responses.GET, RANDOM_IMAGE_URI, json=build_dog("", success=True))
    clazz = DogPhotos(bot)
    with pytest.raises(RuntimeError):
        clazz.get_dog_image()
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == RANDOM_IMAGE_URI


def test_get_breeds_success(bot, responses):
    responses.add(responses.GET, LIST_BREEDS_URI, json=build_breeds(success=True))
    clazz = DogPhotos(bot)
    response = clazz.get_breeds()
    assert response == ["collie", "border collie", "dog"]
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == LIST_BREEDS_URI


def test_get_breeds_failure(bot, responses):
    responses.add(responses.GET, LIST_BREEDS_URI, json=build_breeds(success=False))
    clazz = DogPhotos(bot)
    with pytest.raises(RuntimeError):
        clazz.get_breeds()
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == LIST_BREEDS_URI


@pytest.mark.asyncio
async def test_dog_no_breed(bot, context, responses):
    responses.add(responses.GET, RANDOM_IMAGE_URI, json=build_dog("result", success=True))
    clazz = DogPhotos(bot)
    await clazz.dog(context, None)
    context.send.assert_called_once_with("result")
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == RANDOM_IMAGE_URI


@pytest.mark.asyncio
async def test_dog_known_breed(bot, context, responses):
    responses.add(responses.GET, LIST_BREEDS_URI, json=build_breeds(success=True))
    responses.add(responses.GET, "https://dog.ceo/api/breed/collie/images/random", json=build_dog("pup", success=True))
    clazz = DogPhotos(bot)
    await clazz.dog(context, "collie")
    context.send.assert_called_once_with("pup")
    assert len(responses.calls) == 2
    assert responses.calls[0].request.url == LIST_BREEDS_URI
    assert responses.calls[1].request.url == "https://dog.ceo/api/breed/collie/images/random"


@pytest.mark.asyncio
async def test_dog_unknown_breed(bot, context, responses):
    responses.add(responses.GET, LIST_BREEDS_URI, json=build_breeds(success=True))
    responses.add(responses.GET, RANDOM_IMAGE_URI, json=build_dog("flup", success=True))
    clazz = DogPhotos(bot)
    await clazz.dog(context, "who?")
    context.send.assert_called_once_with("flup")
    assert len(responses.calls) == 2
    assert responses.calls[0].request.url == LIST_BREEDS_URI
    assert responses.calls[1].request.url == RANDOM_IMAGE_URI


def build_dog(img, success):
    return {"message": img, "status": "success" if success else "failure"}


def build_breeds(success):
    return {"message": {"collie": ["border"], "dog": []}, "status": "success" if success else "failure"}
