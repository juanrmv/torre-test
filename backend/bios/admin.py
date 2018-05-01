from django.contrib import admin

# Register your models here.
from bios.models import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_per_page = 25

    actions = None

    list_display = ('first_name', 'last_name', 'status')
