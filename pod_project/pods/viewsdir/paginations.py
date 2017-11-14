# PAGINATIONS

def get_pagination(page, paginator):
    try:
        page = int(page.encode('utf-8'))
    except:
        page = 0
    try:
        return paginator.page(page + 1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        return paginator.page(paginator.num_pages)