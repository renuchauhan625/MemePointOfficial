import random, string, requests, json

from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, TemplateView
from django.shortcuts import render
from accounts.models import UserProfile
   
def display_cookie(request):
    cookie_value = request.COOKIES['my_cookie']
    
    response = requests.get('https://api.imgflip.com/get_memes')
    global memes
    memes = random.sample([ meme for meme in json.loads(response.text)['data']['memes'] ],5)
    print(memes)
    memes_arr = { meme['url']:''.join([str(i) for i in range(0,meme["box_count"])]) for meme in memes }
    print(memes_arr)
    username = request.user.username
    UserProfile.objects.get_or_create(user=request.user)
    user = User.objects.get(username=username)
    consent_obj = user.profile
    consent_obj.consent = True
    
    user.save()
    consent_obj.save()
    return render(request, 'home.html',{'cookie_value':cookie_value, 'memes_url':memes_arr, 'hide_consent': True})

class LoginUser(LoginView):
    template_name = 'login.html'


class HomeView(TemplateView):
    template_name = 'home.html'
        
    def get(self, request):
        response = render(request, 'home.html')
        cookie_string = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        response.set_cookie('my_cookie', cookie_string)    
        return response


class MemeView(TemplateView):
    template_name = 'meme.html'
      
    def __get_rendered_meme__(self, meme_id, meme_url, box_details):
        imgflip_user = "BeastTerrorOfficial"
        imgflip_pass = "Champion1996."
        URL = 'https://api.imgflip.com/caption_image'
        print(box_details)
        params = {
            'username':imgflip_user,
            'password':imgflip_pass,
            'template_id':meme_id,
        }
        counter = 0
        for box in box_details:
            params['boxes[{0}][text]'.format(counter)] = box
            counter +=1
        response = requests.request('POST',URL,params=params).json()
        return response['data']['url']
        
        
    def get(self, request, meme_url, box_count):
            
        boxes = [ request.GET.get("box{0}".format(box_num)) for box_num in box_count ]
        if None not in boxes:
            for meme in memes:
                print(str(meme["url"]), str(meme_url))
                if str(meme["url"]) == str(meme_url):
                    meme_url= self.__get_rendered_meme__(meme["id"],meme_url, boxes)
        response = render(request, 'meme.html', context={'meme_url':meme_url,'box_count':box_count})
        return response
    

    
    