from django.contrib import admin
from .models import Artwork, Keyword, Player, PlayerWord, Category

# Register all models associated with this application
admin.site.register(Artwork)
admin.site.register(Keyword)
admin.site.register(Player)
admin.site.register(PlayerWord)
admin.site.register(Category)
