from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .forms import NewUserForm, LoginForm, MovieForm, CommentForm, MovieSearchForm
from .models import Movie, Genre, Rating, Comment
from django.db.models import Avg


def movie_search_view(request):
    form = MovieSearchForm(request.GET)

    if form.is_valid():
        title = form.cleaned_data.get('title')
        genre = form.cleaned_data.get('genre')
        min_rating = form.cleaned_data.get('min_rating')

        # Perform the movie search based on the form data
        # You can use the provided filters to query the Movie model

        # Example query:
        movies = Movie.objects.all()
        if title:
            movies = movies.filter(title__icontains=title)
        if genre:
            movies = movies.filter(genres=genre)
        if min_rating:
            movies = movies.filter(rating__value__gte=min_rating)
    else:
        movies = Movie.objects.all()

    context = {
        'form': form,
        'movies': movies,
    }

    return render(request, 'userview/movie_search.html', context)


class HomeView(generic.ListView):
    template_name = 'userview/home.html'
    context_object_name = 'movies'

    def get_queryset(self):
        return Movie.objects.annotate(avg_rating=Avg('rating__value')).order_by('-avg_rating')[:5]


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = Comment.objects.filter(movie=self.get_object())
        context['comments'] = comments


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
        return render(request=request, template_name="userview/register.html",
                      context={"register_form": form})
    else:
        form = NewUserForm()
        return render(request=request, template_name="userview/register.html",
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
                return redirect("home")  # Replace 'home' with the name of your home page URL pattern
            else:
                form.add_error(None, 'Invalid username or password.')
                return redirect("index")
        else:
            form.add_error(None, 'Invalid username or password.')
            return redirect("login")
    else:
        user = request.user
        if user.is_authenticated:
            return redirect("home")
        form = LoginForm()
        return render(request=request, template_name="userview/login.html",
                      context={"login_form": form})


@csrf_exempt
def logout_request(request):
    logout(request)
    return redirect('login')


@csrf_exempt
def rate_movie(request, pk):
    movie = get_object_or_404(Movie, pk=pk)

    comments = Comment.objects.filter(movie=movie)
    comment_form = CommentForm(initial={'user': request.user.username})
    if request.method == 'POST':
        if "rate" in request.POST:
            rating_value = int(request.POST.get('rating'))
            rating = Rating(movie=movie, user=request.user, value=rating_value)
            rating.save()
            return redirect('movie', pk=pk)

        elif "comment" in request.POST:
            comment_form = CommentForm(request.POST, initial={'user': request.user.username})
            if comment_form.is_valid():

                comment = comment_form.save(commit=False)

                # class Comment(models.Model):
                #     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
                #     user = models.ManyToManyField(settings.AUTH_USER_MODEL)
                #     text = models.CharField(max_length=1000)
                #     date = models.DateTimeField()
                comment = Comment(movie=movie, text=request.POST.get('text'))
                comment.save()
                comment.user.add(request.user)

                return redirect('movie', pk=pk)

    return render(request, 'userview/movie.html',
                  {'movie': movie, 'comment_form': comment_form, "pk": pk, "comments": comments})


@csrf_exempt
def edit_movie(request, movie_id):
    if not request.user.is_superuser:
        return redirect("index")

    movie = get_object_or_404(Movie, pk=movie_id)

    if request.method == 'POST':
        form = MovieForm(request.POST, instance=movie)
        if form.is_valid():
            edited_movie = form.save()
            return redirect('movie', movie_id=edited_movie.id)
    else:
        form = MovieForm(instance=movie)

    return render(request, 'userview/edit_movie.html', context={'form': form})
