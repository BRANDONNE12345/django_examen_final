from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Article, Commentaire
from .forms import ArticleForm, CommentaireForm
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

def index(request):
    articles_recents = Article.objects.filter(est_publie=True).order_by('-date_de_publication')[:3]
    return render(request, 'index.html', {'articles_recents': articles_recents})

def article_list(request):
    if request.user.is_authenticated and request.user.is_superuser:
        articles = Article.objects.all()
    else:
        articles = Article.objects.filter(est_publie=True)
    return render(request, 'article_list.html', {'articles': articles})

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if not article.est_publie and not (request.user.is_authenticated and (request.user.is_superuser or request.user == article.auteur)):
        return HttpResponseForbidden("Cet article n'est pas encore validé.")
    
    commentaires = article.article_commentaire_ids.all()
    commentaire_form = CommentaireForm()
    return render(request, 'article_detail.html', {
        'article': article,
        'commentaires': commentaires,
        'commentaire_form': commentaire_form
    })

@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.auteur = request.user
            article.est_publie = False
            article.save()
            form.save_m2m()
            messages.success(request, "Votre article a été enregistré en brouillon.")
            return redirect('blog:article_detail', slug=article.slug)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = ArticleForm()
    return render(request, 'article_form.html', {'form': form})

@login_required
def article_update(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.user != article.auteur and not request.user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas la permission de modifier cet article.")
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre article a été modifié avec succès.")
            return redirect('blog:article_detail', slug=article.slug)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = ArticleForm(instance=article)
    return render(request, 'article_form.html', {'form': form})

@login_required
def article_delete(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.user != article.auteur and not request.user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas la permission de supprimer cet article.")
    if request.method == 'POST':
        article.delete()
        messages.success(request, "Votre article a été supprimé avec succès.")
        return redirect('blog:my_article')
    return render(request, 'article_confirm_delete.html', {'article': article})

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def publish_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    article.est_publie = True
    article.save()
    return redirect('blog:article_detail', slug=article.slug)

@login_required
def add_comment(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.method == 'POST':
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.auteur = request.user
            commentaire.article = article
            commentaire.save()
    return redirect('blog:article_detail', slug=article.slug)

def blog(request):
    if request.user.is_authenticated and request.user.is_superuser:
        articles = Article.objects.all()
    else:
        articles = Article.objects.filter(est_publie=True)
    return render(request, 'blog.html', {'articles': articles})

@login_required
def my_article(request):
    articles = Article.objects.filter(auteur=request.user)
    return render(request, 'my_article.html', {'articles': articles})
