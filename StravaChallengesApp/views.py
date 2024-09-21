# strava_integration/views.py

from django.shortcuts import redirect, render, HttpResponseRedirect
from django.http import HttpResponse
import requests
from django.conf import settings
from datetime import datetime
from .models import Activity, Athlete


def login(request):
    # Redirect the user to Strava's authorization endpoint
    authorize_url = (
        f'https://www.strava.com/oauth/authorize?'
        f'client_id={settings.STRAVA_CLIENT_ID}&'
        f'redirect_uri={settings.STRAVA_REDIRECT_URI}&'
        f'response_type=code&'
        f'scope=activity:read_all'
    )
    return redirect(authorize_url)

def auth_callback(request):
    # Retrieve the authorization code from the callback URL
    code = request.GET.get('code')

    # Exchange the code for an access token
    token_data = {
        'client_id': settings.STRAVA_CLIENT_ID,
        'client_secret': settings.STRAVA_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }

    response = requests.post('https://www.strava.com/oauth/token', data=token_data)
    token_json = response.json()

    # Store the access token in the session
    request.session['access_token'] = token_json['access_token']
        
    return render(request, 'StravaChallengesApp/confirmationPage.html')
                  
    
                      
def get_stats(request):
    # Check if the user is authenticated
    if 'access_token' not in request.session:
        return redirect('login')

    # Get the user's access token from the session
    access_token = request.session['access_token']

    # Make a request to fetch the user's activities
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://www.strava.com/api/v3/athletes/18772666/stats', headers=headers)

    if response.status_code == 200:
        activities = response.json()
        return HttpResponse(f'Your stats: {activities}')
    else:
        return HttpResponse('Error fetching activities')


    
def main_page(request):
    return render(request, 'StravaChallengesApp/mainPage.html')

def confirmation_page(request):
    return render(request, 'StravaChallengesApp/confirmationPage.html')

def get_athlete_and_stats(request):
    
    # Check if the user is authenticated
    if 'access_token' not in request.session:
        return redirect('login')

    # Get the user's access token from the session
    access_token = request.session['access_token']

            
    # COLLECT DATA FROM API - Make a request to fetch the user's ACTIVITIES
    headers = {'Authorization': f'Bearer {access_token}'}
    
    SINCE_WHAT_DATE = '2024-01-01T00:00:00Z'       

    
    sinceWhenTimestamp = datetime.strptime(SINCE_WHAT_DATE, '%Y-%m-%dT%H:%M:%SZ')
    epochTimeTimestamp = sinceWhenTimestamp.timestamp()
    
    all_activities = []
    pageIndex = 1
    
    while True:
        params = {
        'after': epochTimeTimestamp,
        'per_page': 200,
        'page': pageIndex
    }        
        
        response = requests.get('https://www.strava.com/api/v3/athlete/activities', headers=headers, params=params)
        
        if response.status_code == 200:
            activity = response.json()
            if not activity:
                break
            all_activities.extend(activity)
            pageIndex += 1
        else:
            print(f'Error fetching activities: Status code {response.status_code}, Response content: {response.text}')
            return HttpResponse(f'Error fetching activities: Status code {response.status_code}, Response content: {response.text}')
    
    #creating a dictionary and counter for outdoor activities
    OUTDOOR_ACTIVITIES_TYPES = ["Walk", "Ride", "AlpineSki", "Swim", "Run", "VirtualRide", "Snowboard", "Hike", "StandUpPaddling", "Windsurf", "Kayaking"]
    activitySummary = dict()
    for acType in OUTDOOR_ACTIVITIES_TYPES:
        activitySummary[acType] = 0
    
    weightTrainingCounter = 0
    
    #going through activities and saving to database
    for outdoorActivity in all_activities:
        print(outdoorActivity)
        activity_type_fetched = outdoorActivity['type']
        activity_distance_fetched = outdoorActivity['distance']
        activity_athlete_fetched  = outdoorActivity['athlete']['id']
        activity_id_fetched = outdoorActivity['id']
        activity_start_date_fetched = outdoorActivity['start_date'][0:10]
        
        try: 
            Activity.objects.get(activity_id = activity_id_fetched)
            
        except:            
            activity_to_be_saved = Activity(activity_athlete = activity_athlete_fetched,
                                            activity_id = activity_id_fetched,
                                            activity_type = activity_type_fetched,
                                            start_date = activity_start_date_fetched,
                                            distance = activity_distance_fetched)
            activity_to_be_saved.save()
        
        if outdoorActivity['type'] in OUTDOOR_ACTIVITIES_TYPES:
            activitySummary[outdoorActivity['type']] += int(outdoorActivity['distance'])
        else:
            weightTrainingCounter += 1     

     
    
     # Make a request to fetch ATHLETE
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://www.strava.com/api/v3/athlete', headers=headers)
    
    if response.status_code == 200:
        athleteData = response.json()        
        global athlete_id_fetched
        athlete_id_fetched = athleteData['id']        
        firstname_fetched = athleteData['firstname']
        lastname_fetched = athleteData['lastname']
        sex_fetched = athleteData['sex']
        photo_medium_url_fetched = athleteData['profile_medium']
        photo_large_url_fetched = athleteData['profile']
        
        totalDistance = sum(activitySummary.values())
        
        # Store Athlete data in session cookie
        request.session['athlete_id_cookie'] = athlete_id_fetched
        request.session['athlete_firstname_cookie'] = firstname_fetched
        request.session['athlete_lastname_cookie'] = lastname_fetched
        
        # Store Athlete data in database
        try:  
            current_athlete = Athlete.objects.get(athlete_id = athlete_id_fetched) #check if athlete in datasbase positivie = saving activity only
            current_athlete.total_ytd_distance = int(totalDistance/1000)
            current_athlete.ride_ytd_distance = int(activitySummary['Ride']/1000)+int(activitySummary['VirtualRide']/1000)
            current_athlete.run_ytd_distance = int(activitySummary['Run']/1000)
            current_athlete.walk_ytd_distance = int(activitySummary['Walk']/1000)+int(activitySummary['Hike']/1000)
            current_athlete.swim_ytd_distance = int(activitySummary['Swim']/1000)+int(activitySummary['StandUpPaddling']/1000)+int(activitySummary['Windsurf']/1000)+int(activitySummary['Kayaking']/1000)
            current_athlete.ski_ytd_distance = int(activitySummary['AlpineSki']/1000)+int(activitySummary['Snowboard']/1000)
            current_athlete.save()
            
        except Athlete.DoesNotExist: #athlete not in database - adding athlete
            username_fetched = athleteData['username']
            
            if username_fetched is None: #avoiding None field value
                username_fetched = 'brak'            
            
            athlete_to_be_saved = Athlete(athlete_id = athlete_id_fetched,
                                          username = username_fetched,
                                          firstname = firstname_fetched,
                                          lastname = lastname_fetched,
                                          sex = sex_fetched,
                                          photo_medium_url = photo_medium_url_fetched,
                                          photo_large_url = photo_large_url_fetched,
                                          total_ytd_distance = int(totalDistance/1000),
                                          ride_ytd_distance = int(activitySummary['Ride']/1000)+int(activitySummary['VirtualRide']/1000),
                                          run_ytd_distance = int(activitySummary['Run']/1000),
                                          walk_ytd_distance = int(activitySummary['Walk']/1000)+int(activitySummary['Hike']/1000),
                                          swim_ytd_distance = int(activitySummary['Swim']/1000)+int(activitySummary['StandUpPaddling']/1000)+int(activitySummary['Windsurf']/1000)+int(activitySummary['Kayaking']/1000),
                                          ski_ytd_distance = int(activitySummary['AlpineSki']/1000)+int(activitySummary['Snowboard']/1000))
            
            athlete_to_be_saved.save()
       
    
    return HttpResponseRedirect('/y5k_results_page')


def y5k_results_page(request):
    athletes = Athlete.objects.order_by('-total_ytd_distance')
    activities = Activity.objects.all()
    athletes_list = []
    athletes_distance = []
    colors_list = []
    border_colors_list = []
    corrected_distance = {}
    
    
    #try:
    #    print(athlete_id_fetched, ' to jest athlete id_fetched')
    #except Exception as e:
    #    print('we have a following error', e)
    
    dataSet = Athlete.objects.order_by('-total_ytd_distance')
    for data in dataSet:
        # here we create lists for chart with regular count of kms
        athletes_list.append(f"{data.firstname}")
        athletes_distance.append(data.total_ytd_distance)
        
        # here we create lists for chart with kms multiplied by effort factor
        walk = int(data.walk_ytd_distance*1.68)
        run = int(data.run_ytd_distance*2.53)
        swim = int(data.swim_ytd_distance*4.98)
        ski = int(data.ski_ytd_distance*0.44)        
        newTotalYtdDistance = walk+run+swim+ski+int(data.ride_ytd_distance)        
        corrected_distance[data.athlete_id] = [data.firstname, data.lastname, newTotalYtdDistance, data.ride_ytd_distance, walk, run, swim, ski, data.last_modified]
        if newTotalYtdDistance >= 5000:
            colors_list.append('green')
        else:
            colors_list.append('orange')
        if data.athlete_id == str(request.session.get('athlete_id_cookie')):
            border_colors_list.append('red')
        else:
            border_colors_list.append('darkorange')
    
    corrected_distance_sorted = dict(sorted(corrected_distance.items(), key=lambda item: item[1][2], reverse=True))
    #print(corrected_distance_sorted)
    
    athletes_list_corrected = [details[0] for details in corrected_distance_sorted.values()]
    #print(athletes_list_corrected)
    
    athletes_distance_corrected = [details[2] for details in corrected_distance_sorted.values()]
    #print(athletes_distance_corrected)
        
        #try:
        #    if athlete_id_fetched == int(data.athlete_id):
        #        colors_list.append('red')
        #    else:
        #        colors_list.append('orange')
        #except:
    
    MONTHS_LIST = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Grudzień']
    
    
    return render(request, 'StravaChallengesApp/y5kResultsPage.html',{
        'athletes': athletes,
        'activities': activities,
        'athletes_list': athletes_list,
        'athletes_distance': athletes_distance,
        'colors_list': colors_list,
        'border_colors_list': border_colors_list,
        'athletes_list_corrected': athletes_list_corrected,
        'athletes_distance_corrected': athletes_distance_corrected,
        'corrected_distance': corrected_distance_sorted,
        'months_list': MONTHS_LIST,
        'athlete_firstname_cookie' : request.session.get('athlete_firstname_cookie', ' '),
        'athlete_lastname_cookie' : request.session.get('athlete_lastname_cookie', ' '),
        'athlete_id_cookie' : str(request.session.get('athlete_id_cookie', ' nieznajomy(a) '))
    })