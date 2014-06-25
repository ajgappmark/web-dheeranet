from flask import Blueprint, render_template, abort, redirect
from jinja2 import TemplateNotFound
from dheeranet import static_bucket
from dheeranet.cache import cached, s3_get_cached
from ast import literal_eval
import json

pages = Blueprint('pages', __name__,template_folder='../template')

@pages.route('/<path:path>')
def show(path):
  try:

    page = get_page(path)
    if not page:
      abort(404)

    subnavbar = get_subnavbar(path)

    params_json, content = page.split('\n\n',1);
    params = json.loads(params_json)

    if params['redirect']:
      return redirect(params['redirect'])

    if 'title' not in params:
      params['title'] = ''

    if 'subtitle' not in params:
      params['subtitle'] = ''

    return render_template(
      'page.html',
      title=params['title'],
      subtitle=params['subtitle'],
      content=content,
      subnavbar=subnavbar
    )

  except IOError:
    abort(404)


@cached()
def get_page(path):
  page = s3_get_cached(static_bucket, 'pages/' + path)
  if not page:
    page = s3_get_cached(static_bucket, 'pages/' + path + '/__index__')
  return page

@cached()
def get_subnavbar(path):

  path = path.strip('/')

  subnavbar = s3_get_cached(static_bucket, 'pages/' + path + '/__nav__')

  if not subnavbar:
    path_trunc = path[0:path.rfind('/')]
    subnavbar = s3_get_cached(static_bucket, 'pages/' + path_trunc + '/__nav__')

  if subnavbar:
    return json.loads(subnavbar)

  else:
    return []
