from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm, KeywordForm
from .models import Artwork, Player, Keyword, PlayerWord, Category
from .bad_words import bad_word_list

# View function that renders the home page
def index(request):
  return render(request, 'game/home.html')

# View function that renders the about page
def about(request):
  return render(request, 'game/about.html')

# View function that handles requests for user profile
def profile(request):
  p = Player.objects.get(username=request.user.username)
  return render(request, 'game/profile.html', locals())

# View function that pulls the list of players and sends it to the rendering of the leaderboard page
def leaderboard(request):

  # Pull the list of all players registered in the database
  player_list = Player.objects.all()
  player_list = player_list[:10]

  # Send the list of all players to render in the leaderboard page
  return render(request, 'game/leaderboard.html', locals())


def initgame(request):
    if request.user.is_authenticated:
        
        p = Player.objects.get(username=request.user.username)
        p.newGame()
        request.session['error_flag'] = 0
        if request.method == 'POST':
          c = request.POST.get('category', False)
          if c is "":
            pass
          elif int(c) != -1 :
            p.setCategory(int(c))
            return HttpResponseRedirect('/game/')
        p.setCategoryNull()
        return HttpResponseRedirect('/game/')
    return HttpResponseRedirect('/')


# View function that handles game functionality
def game(request):

    # If the request is coming from a user that is logged in
    if request.user.is_authenticated:

        p = Player.objects.get(username=request.user.username)
        c_list = Category.getCategoryList()

        # Load the next artwork that the player should label
        img = p.next_art
        t = p.curr_timer

        #if POST request, then the data was just submitted to form
        if request.method == 'POST':
            error_flag = 0
            # Load the keyword form
            k_form = KeywordForm(request.POST)
            t = request.POST.get('timer', False)

            if int(t) == 0:
                p.finishImage()
            else:

                #update players time remaining
                p.setTime(t)

                # If the keyword form is valid
                if k_form.is_valid():
                    word = k_form.cleaned_data.get('k_text')

                    # If the word is not a bad word
                    if (not checkWord(word)):

                        # If the player has not already provided this word for the image
                        if (not PlayerWord.check_dup(word, p)):

                            # Submit the word to the database and return the score
                            x = p.submitWord_getScore(word, img) 

                        # If the Player has already provided this word for this image
                        else: error_flag=1
                        # If the word is a bad word
                    else: error_flag=2
                else: error_flag=3

            # If the form is not valid, redirect back to the game
            request.session['error_flag'] = error_flag
            return redirect('/game/')

        
        error_flag = request.session.get('error_flag')
        #print(error_flag)
        # If not POST request, render empty form, image for input
        k_form = KeywordForm()

        # Put the submitted words
        p_words = PlayerWord.getWords(p)
        height = int((350.0/float(img.artwork_image.width))*img.artwork_image.height) 

        # Render the game view passing in the image, the keyword form and the list of labes
        return render(request, 'game/game.html', {'image': img, 'k_form': k_form, 'p_words': p_words, 'curr_time': t, 'p': p, 'c_list': c_list, 'height': height, 'error_flag': error_flag})

    # If the user is not authenticated, redirect is to home page
    else:
      return HttpResponseRedirect('/')
    #if HttpRequest.is_ajax():

# View function that checks is a submitted label is considered innapropriate
def checkWord(word):

  # List of unacceptable words
  
  # if the word is in the list, return true
  if word in bad_word_list:
    return True

  # if the word is not in the list, return false
  else:
    return False


def descriptor(request):
  form = DescriptorForm(request.POST or None)
  if form.is_valid():
    keyword = form.save(commit=False)
    descriptor = form.cleaned_data.get('descriptor')
    Keyword.addKeyword(descriptor)
    if keyword is not None:
      return render(request, 'game/game.html', {'form': form})
  return render(request, 'game/game.html', {'form': form})

# View function that handles user registration
def register(request):

  # Load in the user registration form
  form = RegisterForm(request.POST or None)

  # If the form is valid
  if form.is_valid():

    # Save the form
    user = form.save(commit=False)

    # Extract username and password
    username = form.cleaned_data.get('username')
    password = form.cleaned_data.get('password')

    # Associate the indicated password with the user
    user.set_password(password)

    # Save the user
    user.save()

    # Add the newly register user to the Player table
    Player.addPlayer(username)
    user = authenticate(username=username, password=password)

    # If the user is not empty
    if user is not None:

      # If the user already has an account
      if user.is_active:

        # Login the user and redirect them to game
        login(request, user)
        return HttpResponseRedirect('/initgame/')

  # Once a user is registered, send them to game portal
  return render(request, 'game/register.html', {'form': form})

