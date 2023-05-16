from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, get_object_or_404, redirect

from django.http import HttpRequest, HttpResponse


from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from .forms import NewUserForm, LoginForm
from .models import Movie, Genre, Rating

# def index(request : HttpRequest):
#     movies = Movie.objects.order_by('-title')
#     template = loader.get_template('userview/index.html')
#     context = {
#     'movies' : movies
#     }
#     return HttpResponse(template.render(context,request))

# def view_movie(request: HttpRequest, movie_id):
#     response = 'you are looking at the movie with an id %s'
#     return HttpResponse(response % movie_id)

# def view_genre(request: HttpRequest, genre_id):
#     response = 'you are looking at the genre with an id %s'
#     return HttpResponse(response % genre_id)


from django.views import generic

class IndexView(generic.ListView):
    template_name = 'userview/index.html'
    context_object_name = 'movies'
    paginate_by = 2

    def get_queryset(self):
        return Movie.objects.order_by('-title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            user_rated_movies = Rating.objects.filter(user=user).values_list('movie', flat=True).distinct()
            movies = Movie.objects.filter(pk__in=user_rated_movies)
            context['user_rated_movies'] = movies
            return context


class MovieView(generic.DetailView):
    model = Movie
    template_name = 'userview/movie.html'

class GenreView(generic.DetailView):
    model = Genre
    template_name = 'userview/genre.html'


@csrf_exempt
def register_request(request):

    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
        return render (request=request, template_name="userview/register.html",
            context={"register_form": form})
    else:
        form = NewUserForm()
        return render (request=request, template_name="userview/register.html",
            context={"register_form": form})


@csrf_exempt
def login_request(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Log the user in
                login(request, user)
                return redirect("index")  # Replace 'home' with the name of your home page URL pattern
            else:
                form.add_error(None, 'Invalid username or password.')
                return redirect("index")
        else:
            form.add_error(None, 'Invalid username or password.')
            return redirect("index")
    else:
        user = request.user
        if user.is_authenticated:
            return redirect("index")
        form = LoginForm()
        return render (request=request, template_name="userview/login.html",
            context={"login_form": form})


@csrf_exempt
def logout_request(request):
    logout(request)
    return redirect('login')


@csrf_exempt
def rate_movie(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    rating_value = int(request.POST.get('rating'))
    rating = Rating(movie=movie, user=request.user, value=rating_value)
    rating.save()
    return redirect('movie', pk=pk)
