from django.db import models
from django.utils import timezone
from django.db.models.aggregates import Count
from django.core.files import File
from random import randint
import random, os

#For initial bulk upload
BULK_UPLOAD_ROOT = '/home/turneyn/images/'

TIME_PER_IMAGE = 60

FIRST_PERCENTILE = 20
SECOND_PERCENTILE = 40
THIRD_PERCENTILE = 60

FIRST_TIER_POINTS = 20
SECOND_TIER_POINTS = 10
THIRD_TIER_POINTS = 5

# Database schema for Category model
class Category (models.Model):

  #id = models.BigIntegerField(primary_key = True)
  category_name = models.CharField("CategoryName", max_length=50)

  # Method that adds a category name to the category field
  def addCategory(category):
    cat = Category(category_name = category)
    cat.save()
    return cat

  # Method that returns the list of all categories
  def getCategoryList():
    c_list = Category.objects.all()
    return c_list

  # Method that returns the ID associated with category name
  def getCategory(categoryString):
    if(Category.objects.filter(category_name = categoryString).exists()):
      cat = Category.objects.get(category_name = categoryString)
      return cat
    else:
      return Category.addCategory(categoryString)

# Method that returns current date/time
def getCurrentTime():
        return timezone.now()

#Database schema for artwork to be used in game
class Artwork (models.Model):

    #id = models.AutoField(primary_key=True) **implicitly defined

    # artwork_image attribute is the artword that was uploaded to MEDIA_ROOT/artwork
    artwork_image = models.ImageField("Image", upload_to='artwork/')

    # up_date attribute gets current date as upload time
    up_date = models.DateTimeField("Date uploaded", default=getCurrentTime)

    category = models.ForeignKey(to=Category, blank=True, null=True, on_delete=models.SET_NULL)

    # Returns the self association
    def __str__(self):
        return str(self.id)

    # Method that 
    def addFromCSV(folder, fileName):

        # Open a file as read only
        with open(fileName, "r") as f:

            # Read the file and store it as data
            data = f.read()

            # Split lines in data into array
            lines = data.split("\n")
            try:     
                for line in lines:
                    entries = line.split(",")
                    cat = Category.getCategory(entries[1])
                    a = Artwork(category=cat)
                    path = os.path.join(folder, entries[0])
                    a.artwork_image.save(entries[0], open(os.path.join(BULK_UPLOAD_ROOT, path), "rb"))
                    a.save()
            except IndexError:
                pass
        f.close()

    # Metadata for the database Artwork Model
    class Meta:

        # Sets default ascending ordering by id
        ordering = ["id"]

# Keyword Model for all user generated models
class Keyword (models.Model):

    # artwork attribute is the ID from the artwork model
    artwork = models.ForeignKey(to=Artwork, on_delete=models.CASCADE)

    # work attribute is the keyword field form the form
    word = models.CharField("Keyword", max_length=50)

    # count attribute keeps track of the frequency of label
    count = models.PositiveIntegerField("Frequency", default=0)

    # Self method that returns keyword list
    def __str__(self):
        return self.word

    # Method that adds the keyword to the associated artwork model
    def addKeyword(inputWord, targetArt):

      # Associate keyword to the corresponding artwork model
      k=Keyword(word = inputWord, artwork=targetArt)

      # Save the associated keyword model
      k.save()

    # Method that returns the queryset of Keywords for given image
    def words_for_image(img):
        return Keyword.objects.filter(artwork=img)

    # Method that returns true if the word already exists for a given image, false if not
    def check_dup(the_word, img):
        return Keyword.words_for_image(img).filter(word=the_word).exists()

    # Method that checks if a word is present for an artwork model and increments it if it is
    def inc_count(the_word, img):

        # If word is present for artwork, otherwise this would crash
        if(Keyword.check_dup(the_word, img)):

            # Get the word from the Keyword model, increment count, save the model
            w = Keyword.words_for_image(img).filter(word=the_word).first()
            w.count+=1
            w.save()

    def calcScore(the_word, img):
        c = Keyword.objects.filter(artwork=img, word=the_word).first().count
        i = 1
        qs = Keyword.objects.filter(artwork=img).order_by('-count').distinct('count')
        tot = qs.count()
        for e in qs:
            if c >= e.count:
                break
            i += 1
        if tot < 3:
            return THIRD_TIER_POINTS
        p = int((float(i)/float(tot)) * 100)
        if p < FIRST_PERCENTILE:
            return FIRST_TIER_POINTS
        elif p < SECOND_PERCENTILE:
            return SECOND_TIER_POINTS
        elif p < THIRD_PERCENTILE: 
            return THIRD_TIER_POINTS
        else:
            return 1

    # Method that adds a Keyword to an Artwork model
    def addWord_getScore(the_word, img):

        #If the Keyword is already associated with the Artwork, increment its count
        if (Keyword.check_dup(the_word, img)):
            Keyword.inc_count(the_word, img)

        #If the Keyword is not associated with the Artwork, add it to the Artwork
        else:
            Keyword.addKeyword(the_word, img)

        # Return the  frequency for associations
        return Keyword.calcScore(the_word, img)

# Method that is called as default for Player Creation or Artwork Deletion which selects a random Artwork as a starting point
def randomArt():

    # Get the count of rtwork object models
    count = Artwork.objects.aggregate(count=Count('id'))['count']

    # Generate a random index to start at
    random_index = randint(0, count - 1)

    # Pull the Artwork Model at that random index
    art = Artwork.objects.all()[random_index]

    # Return the associated Artwork Id
    return art.id 

# Moodel that creates players
class Player (models.Model):


    # username attribute is the username the user created upon account creation 
    username = models.CharField("User Name", primary_key=True, max_length=50)

    # next_art attribute is the ID of the Artwork model they will label next
    next_art = models.ForeignKey(to=Artwork,
                                 default=randomArt, 
                                 on_delete=models.SET(randomArt)
                                )

    # total_score attribute is the total amount of points a Player has accumulated
    total_score = models.PositiveIntegerField("Total Score", default=0)

    # high_score attribute is the high score of the user
    high_score = models.PositiveIntegerField("High Score", default=0)

    # games_played attribute is the number of total images labeled by the user
    games_played = models.PositiveIntegerField("Games Played", default=0)

    # curr_timer attribute is the remaining time left for an associated Artwork
    curr_timer = models.PositiveIntegerField("Current Time Left", default=60)

    curr_score = models.PositiveIntegerField("Current Game's Score", default=0)

    category = models.ForeignKey(to=Category, blank=True, null=True, on_delete=models.SET_NULL)

    # Method that cycles to the next image
    def nextImage(self):

        # Get the ID of the artwork to cycle to
        num = self.next_art.id +1
        if self.category is None:
            # While the artwork exists and ID is less then next ID
            while (not(Artwork.objects.filter(id=num).exists())) and (num<Artwork.objects.last().id):

                # Increment the artwork ID
                num = num+1

            # If the number is greater than the lat labeled ID
            if num > Artwork.objects.last().id:

                # Increment the next ID
                num = Artwork.objects.first().id
            #print(num)

        else:
            # While the artwork exists and ID is less then next ID
            while (not(Artwork.objects.filter(id=num, category=self.category).exists())) and (num<Artwork.objects.last().id):

                # Increment the artwork ID
                num = num+1

            # If the number is greater than the lat labeled ID
            if num > Artwork.objects.last().id:

                # Increment the next ID
                num = Artwork.objects.filter(category=self.category).first().id
            #print(num)

        
        # The next_art attribute of a user will be the next object
        self.next_art = Artwork.objects.get(id=num)

        # Save state of Player model
        self.save()

        # Return the next image the user will label
        #image = self.next_art
        #return image


    # Method that adds a Player to the model given its username
    def addPlayer(name):
        p = Player(username = name)
        p.save()


    # Method that returns the username in String format of the associated Player model
    def __str__(self):
        return str(self.username)

    # Method that submits the input word to the Keyword model and gets a score for the Keyword
    def submitWord_getScore(self, word, img):

        # Add the keyword to the artwork model and get a score
        x = Keyword.addWord_getScore(word, img)
        
        PlayerWord.addKeyword(self, word, x) 
        # Add the score for that image to the total score and save it
        self.total_score += x
        self.curr_score += x
        if (self.curr_score > self.high_score):
            self.high_score = self.curr_score
        self.save()
        return x

    # Method that returns total scoreof a player
    def getTotalScore(self):
        return self.total_score

    def setTime(self, t):
        self.curr_timer = t
        self.save()

    def resetTime(self):
        self.curr_timer = TIME_PER_IMAGE
        self.save()

    def finishImage(self):
        self.resetTime()
        PlayerWord.ClearWords(self)
        self.nextImage()

    def newGame(self):
        self.games_played += 1
        self.curr_score = 0
        self.finishImage()

    def setCategory(self, category):
        self.category = Category.objects.get(id=category)
        self.save()

    def setCategoryNull(self):
        self.category = None
        self.save()


    # Metadata for Player model
    class Meta:

        # sets default ordering, descending by total_score
        ordering = ["-total_score"]

# Model that associated Players with Word in game functioanlity
class PlayerWord(models.Model):

    # player attribute that associates it to a Player model
    player = models.ForeignKey(to=Player, on_delete=models.CASCADE)

    # word attribute associates the keyword to Player model
    word = models.CharField("Keyword", max_length=50)

    # points attribute that keeps track of total points
    pts = models.PositiveIntegerField("Points", default=0)

    # Method that returns the associated word of the model
    def __str__(self):
        return self.word

    # Method that adds a Keyword to a Player model
    def addKeyword(the_player, inputWord, points):

      # Associate an Keyword, a Player and points with a player - then save it
      k=PlayerWord(word = inputWord, player=the_player, pts=points)
      k.save()

    # Method that gets the total words associated with the player
    def getWords(the_player):
        words = list()

        # For every word the Player has labeled in this picture, append to the word
        for pw in PlayerWord.objects.filter(player=the_player):
            #words.append(pw.word)
            words.append(pw)
        return words

    #returns true if word exists for a given image, false if not
    #takes string and artwork object

    # Method that returns true if the word exists for a given image, and false if not
    def check_dup(the_word, the_player):
        return PlayerWord.objects.filter(player=the_player, word=the_word).exists()

    #Removes PlayerWords associated with the_player
    #For use when image cycles
    def ClearWords(the_player):
        PlayerWord.objects.filter(player=the_player).delete()

# Method that, given a username, increments a players next_art and returns the current artwork to be displayed


