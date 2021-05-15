from discord.http import Route


class Route8(Route):
    BASE = "https://discord.com/api/v8"

    def __eq__(self, other):
        if isinstance(other, Route8):
            return self.method == other.method and self.url == other.url
        return False

    def __str__(self):
        return f"{self.method} {self.url}"

    def __repr__(self):
        return f"{self.method} {self.url}"
