#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Views for sacrud_pages
"""
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config


@view_config(route_name='sacrud_pages_move', renderer='json',
             permission=NO_PERMISSION_REQUIRED)
def page_move(request):
    node = request.matchdict['node']
    method = request.matchdict['method']
    left_sibling = request.matchdict['leftsibling']

    table = request.sacrud_pages_model
    page = request.dbsession.query(table).filter_by(id=node).one()

    if method == 'inside':
        page.move_inside(left_sibling)
    if method == 'after':
        page.move_after(left_sibling)
    return ''


@view_config(route_name='sacrud_pages_get_tree', renderer='json',
             permission=NO_PERMISSION_REQUIRED)
def get_tree(request):
    def fields(node):
        return {'visible': node.visible,
                'CSSredirect': 'jqtree-redirect-%s' % node.redirect_type,
                'redirect': '%s' % (node.redirect or node.redirect_url or '')}
    table = request.sacrud_pages_model
    return table.get_tree(request.dbsession, json=True, json_fields=fields)


@view_config(route_name='sacrud_pages_visible', renderer='json',
             permission=NO_PERMISSION_REQUIRED)
def page_visible(request):
    node = request.matchdict['node']
    table = request.sacrud_pages_model
    node = request.dbsession.query(table).filter_by(id=node).one()
    node.visible = not node.visible
    request.dbsession.add(node)
    request.dbsession.flush()

    return {"visible": node.visible}


@view_config(route_name='sacrud_pages_view', renderer='/sacrud_pages/index.jinja2',
             permission=NO_PERMISSION_REQUIRED)
def page_view(context, request):
    page = context.node

    if not page.visible:
        raise HTTPNotFound

    context = {'page': page,
               'page_resource': context,
               }

    if page.redirect_page:
        if not page.redirect_type or page.redirect_type == '200':
            context['page'] = page.redirect
        else:
            return Response(status_code=int(page.redirect_type),
                            location='/'+page.redirect.get_url())
    if page.redirect_url:
        return Response(status_code=int(page.redirect_type),
                        location=page.redirect_url)
    return context