import pytest
from tests.duckmock.urllib import patch_urlopen
from duckbot.cogs.dogs import DogPhotos


def build_dog(img, success):
    return '{"message": "' + img + '", "status": "' + ("success" if success else "failure") + '"}'


@pytest.mark.asyncio
async def test_get_dog_image_success(bot):
    result = build_dog("dog", True)
    with patch_urlopen(result):
        clazz = DogPhotos(bot)
        response = clazz.get_dog_image()
        assert response == "dog"


@pytest.mark.asyncio
async def test_get_dog_image_failure(bot):
    result = build_dog("dog", False)
    with patch_urlopen(result):
        clazz = DogPhotos(bot)
        with pytest.raises(RuntimeError):
            clazz.get_dog_image()


@pytest.mark.asyncio
async def test_get_dog_image_no_message(bot):
    result = build_dog("", True)
    with patch_urlopen(result):
        clazz = DogPhotos(bot)
        with pytest.raises(RuntimeError):
            clazz.get_dog_image()
