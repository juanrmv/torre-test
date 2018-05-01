from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import api_view

from bios.models import LinkedInProfile, Candidate
from bios.serializers import CandidateSerializer


@api_view(['GET'])
def LinkedAuthURL(request, id):
    from django.conf import settings
    from linkedin_v2 import linkedin

    try:
        return_url = 'http://localhost:8000/api/linkedin/callback/'
        authentication = linkedin.LinkedInAuthentication(settings.LINKEDIN_API_KEY, settings.LINKEDIN_API_SECRET,
                                                         return_url,
                                                         [linkedin.PERMISSIONS.BASIC_PROFILE])
        authentication.state = authentication._make_new_state()
        url = authentication.authorization_url
        candidate = Candidate.objects.get(id=id)
        candidate.temporal_state = authentication.state
        candidate.save()
        return HttpResponseRedirect(url)

    except:
        return HttpResponse("Problems with LinkedinAPI", status=400)


@api_view(['GET'])
def LinkedCallback(request):
    from django.conf import settings
    from linkedin_v2 import linkedin

    try:
        authentication = linkedin.LinkedInAuthentication(settings.LINKEDIN_API_KEY, settings.LINKEDIN_API_SECRET,
                                                         'http://localhost:8000/api/linkedin/callback/',
                                                         [linkedin.PERMISSIONS.BASIC_PROFILE])

        authentication.authorization_code = request.GET.get('code', '')
        accessToken = authentication.get_access_token()

        candidate = Candidate.objects.get(temporal_state=request.GET.get('state', 'dsdsds'))
        LinkedInProfile.objects.filter(candidate=candidate).delete()
        LinkedInProfile.objects.create(candidate=candidate, access_token=accessToken.access_token,
                                       expires_in=accessToken.expires_in)

        return HttpResponse('Todo fino', status=200)

    except Exception as error:
        return HttpResponse("Problems with LinkedinAPI" + repr(error), status=500)


class CandidateViewSet(viewsets.ModelViewSet):
    serializer_class = CandidateSerializer
    queryset = Candidate.objects.all()