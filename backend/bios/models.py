from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Candidate(models.Model):
    STATUSES = [
        (0, 'Created'),
        (1, 'Torre Bio processed'),
        (2, 'Torre Bio failed'),
        (3, 'Linked in Auth'),
        (4, 'Linked in processed'),
        (5, 'Linked in failed'),
        (6, 'Finished'),
        (7, 'Problems with similarity'),
    ]

    status = models.IntegerField(choices=STATUSES, blank=False, null=False, default=0)
    torre_public_id = models.SlugField(null=False, blank=False)
    first_name = models.CharField(null=True, blank=True, max_length=120)
    last_name = models.CharField(null=True, blank=True, max_length=120)
    email = models.EmailField(null=True, blank=True)
    similarity = models.FloatField(null=True, blank=True, default=0)
    error = models.TextField(null=True, blank=True)
    temporal_state = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TorreProfile(models.Model):
    candidate = models.OneToOneField(Candidate, blank=False, related_name='torre_profile', null=False,
                                     on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    jobs_count = models.IntegerField(default=0)
    education_count = models.IntegerField(default=0)


class LinkedInProfile(models.Model):
    access_token = models.TextField(blank=True, null=True)
    expires_in = models.IntegerField(blank=True, null=True)
    candidate = models.OneToOneField(Candidate, blank=False, related_name='linkedin_profile', null=False,
                                     on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    jobs_count = models.IntegerField(default=0)
    education_count = models.IntegerField(default=0)


@receiver(post_save, sender=Candidate)
def post_save_candidate(sender, instance, **kwargs):
    if instance.status == 0:  # Created
        from bios.functions import import_torre_bio
        try:
            profile = import_torre_bio(instance.torre_public_id)
            instance.first_name = profile['first_name']
            instance.last_name = profile['last_name']
            instance.email = profile['email']
            instance.status = 1
            TorreProfile.objects.create(candidate=instance, content=profile['profile'],
                                        jobs_count=profile['jobs_count'], education_count=profile['education_count'])
        except Exception as error:
            instance.status = 2
            instance.error = repr(error)

        instance.save()

    if instance.status == 4:  # Created
        from bios.functions import similarity
        try:
            instance.similarity = similarity(instance.torre_profile, instance.linkedin_profile)
            instance.status = 6
        except Exception as error:
            instance.status = 7
            instance.error = repr(error)

        instance.save()


@receiver(post_save, sender=LinkedInProfile)
def post_save_linked_in_profile(sender, instance, **kwargs):
    if instance.candidate.status == 1:
        from bios.functions import import_linked_in
        try:
            profile = import_linked_in(instance)
            instance.candidate.status = 4
            TorreProfile.objects.create(candidate=instance, content=profile['profile'],
                                        jobs_count=profile['jobs_count'], education_count=profile['education_count'])
        except Exception as error:
            instance.candidate.status = 5
            instance.candidate.error = repr(error)

        instance.candidate.save()
