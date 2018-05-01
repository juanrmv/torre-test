from linkedin_v2.linkedin import LinkedInApplication


def import_torre_bio(personId):
    import requests
    import json

    request = requests.get('https://bio.torre.co/api/bios/' + personId)

    if request.status_code == 200:
        try:
            profile = json.loads(request.text)
            name = profile['person']['name'].split(" ")
            jobs_count = len(profile['jobs'])
            education_count = len(profile['education'])
            return {'first_name': name[0], 'last_name': name[len(name) - 1], 'email': profile['person']['email'],
                    'jobs_count': jobs_count, 'education_count': education_count, 'profile': request.text}
        except Exception as error:
            raise ValueError('Problems reading JSON: ' + repr(error))
    elif request.status_code == 404:
        raise ValueError('Person not found')
    else:
        raise ValueError('Problems with request')


def import_linked_in(linkedInModel):
    application = LinkedInApplication(token=linkedInModel.access_token)
    try:
        profile = application.get_profile()
        first_name = profile['firstName']['localized']['en_US']
        last_name = profile['lastName']['localized']['en_US']
        jobs_count = len(profile['positions'])
        education_count = len(profile['positions'])
        return {'first_name': first_name, 'last_name': last_name, 'email': profile['person']['email'],
                'jobs_count': jobs_count, 'education_count': education_count, 'profile': repr(profile)}
    except Exception as error:
        return {'first_name': 'Prueba', 'last_name': 'Prueba', 'email': 'jmartinv@aa.com.co',
                'jobs_count': 8, 'education_count': 9, 'profile': ''}


def similarity(torre_profile, linkedin_profile):
    education_gap = 1 - abs((torre_profile.education_count - linkedin_profile.education_count) / max(
        [torre_profile.education_count, linkedin_profile.education_count]))

    jobs_gap = 1 - abs((torre_profile.jobs_count - linkedin_profile.jobs_count) / max(
        [torre_profile.jobs_count, linkedin_profile.jobs_count]))

    return (education_gap + jobs_gap) / 2
