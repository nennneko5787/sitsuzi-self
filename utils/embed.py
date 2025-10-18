from curl_cffi import AsyncSession
from discord import Embed


async def embedMaker(embed: Embed, *, silent: bool = False) -> str:
    http = AsyncSession(base_url="https://nemtudo.me/api/")

    response = await http.post(
        "tools/embeds",
        json={
            "title": embed.title,
            "author": embed.author.name if embed.author else None,
            "description": embed.description,
            "image": embed.image.url if embed.image else None,
            "thumbImage": embed.thumbnail.url if embed.thumbnail else None,
            "color": str(embed.color) if embed.color else None,
            "video": embed.video.url if embed.video else None,
        },
    )

    jsonData = response.json()

    if silent:
        return "[󠅺](https://nemtudo.me/e/" + jsonData["data"]["id"] + ")"
    else:
        return "https://nemtudo.me/e/" + jsonData["data"]["id"]
