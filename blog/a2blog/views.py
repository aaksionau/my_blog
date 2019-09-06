from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.core.mail import send_mail
from django.db.models import Count

from taggit.models import Tag

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 5
    template_name = 'a2blog/post/list.html'


class PostFilteredListView(ListView):
    context_object_name = 'posts'
    paginate_by = 5
    template_name = 'a2blog/post/list.html'

    def get_queryset(self):
        tag = get_object_or_404(Tag, slug=self.kwargs['tag'])
        return Post.published.filter(tags__in=[tag])


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published\
        .filter(tags__in=post_tags_ids)\
        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
        .order_by('-same_tags', '-publish')[:4]

    return render(request,
                  'a2blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form,
                   'similar_posts': similar_posts})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} ({cd['email']}) recommends you reading: {post.title}"
            message = f"Read {post.title} \
                        at {post_url} \n\n {cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@myblog.com', (cd['to'],))

            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'a2blog/post/share.html',
                  {'post': post,
                   'form': form,
                   'sent': sent})
