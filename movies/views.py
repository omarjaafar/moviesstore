from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, MovieVote
from django.contrib.auth.decorators import login_required

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie).order_by('-likes', '-date')

    thumbs_up_count = movie.get_thumbs_up_count()
    thumbs_down_count = movie.get_thumbs_down_count()
    user_vote = movie.user_vote(request.user)

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['thumbs_up_count'] = thumbs_up_count
    template_data['thumbs_down_count'] = thumbs_down_count
    template_data['user_vote'] = user_vote
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)


def top_comments(request):
    comments = Review.objects.order_by('-likes')[:10]  # top 10 by likes
    return render(request, 'movies/top_comments.html', {'comments': comments})

@login_required
def like_comment(request, comment_id):
    review = get_object_or_404(Review, id=comment_id)
    review.likes += 1
    review.save()
    return redirect('movies.show', id=review.movie.id)  # back to the movie page

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, movie_id=id)
    review.delete()   # simplest solution: just delete it
    return redirect('movies.show', id=id)

@login_required
def vote_movie(request, id, vote_type):
    movie = get_object_or_404(Movie, id=id)
    existing_vote = MovieVote.objects.filter(user=request.user, movie=movie).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            existing_vote.delete()
        else:
            existing_vote.vote_type = vote_type
            existing_vote.save()
    else:
        MovieVote.objects.create(user=request.user, movie=movie, vote_type=vote_type)
    
    return redirect('movies.show', id=id)
