from django.core.paginator import Paginator


def easy_paginator(sequence, request, amount_posts=10):
    paginator = Paginator(sequence, amount_posts)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
