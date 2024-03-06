from django import template

register = template.Library()


@register.simple_tag
def remove_sum(link):
    return link[2:]


@register.simple_tag
def len_link_remove_sum(link):
    link = link[2:]
    if len(link) > 60:
        parts = [link[i:i + 60] for i in range(0, len(link), 60)]

        link = ' '.join(parts)
    return link


@register.simple_tag
def len_link(link):
    if len(link) > 60:
        parts = [link[i:i + 60] for i in range(0, len(link), 60)]

        link = ' '.join(parts)
    return link
