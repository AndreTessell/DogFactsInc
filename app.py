import logging
# set up the datadog tracer https://docs.datadoghq.com/tracing/setup/python/
from ddtrace import patch_all, tracer, config
import ddtrace

log = logging.getLogger()
log.level = logging.INFO

from flask import Flask, render_template, abort, redirect, flash
import requests
from urlparse import urlparse
import random
import subprocess
import os
import time


app = Flask(__name__)


# the dog image service https://dog.ceo/dog-api/documentation
# the vendor said we could get a specific breed if we changed the url
# DOG_IMAGE_SERVICE = 'https://dog.ceo/api/breed/<breed>/<sub-breed>/images/random'
# e.g.
# DOG_IMAGE_SERVICE = 'https://dog.ceo/api/breed/collie/border/images/random'
DOG_IMAGE_SERVICE = 'https://dog.ceo/api/breeds/image/random'

DOG_FACT_SERVICE = 'http://dog-api.kinduff.com/api/facts'

# https://www.akc.org/most-popular-breeds/2018-full-list/
# but all dogs are good boys
GOOD_BOYS = [
  'labrador',
  'germanshepherd',
  'retriever-golden',
  'bulldog-french',
  'bulldog-english'
]

@tracer.wrap('dog.image', service='dog-image-service', span_type='web')
def dog_image():
  # randomly fail somewhere in here
  if random.randrange(0, 10) == 9:
    app.logger.error('We really should fix this at some point.')
    abort(500, 'Huh, something randomly failed here.')
  dog_image = requests.get(DOG_IMAGE_SERVICE).json()
  image_url = dog_image.get('message')
  app.logger.info('Returned image: %s' % image_url)
  # set the breed at the root span to create a facet on
  breed = extract_breed(image_url)
  root_span = tracer.get_call_context().get_current_root_span()
  root_span.set_tag('breed', breed)
  # find out how big the image is
  size = requests.get(image_url, stream=True).headers['Content-length']
  app.logger.info("File size of image %s" % size)
  # let's grade the image, maybe we should add this to a span somwhere?
  quality = image_quality(size)
  app.logger.info("Image quality is %s" % quality)
  # TODO: we should add the quality as a tag here
  root_span.set_tag('quality', quality)
  return image_url

@tracer.wrap('dog.fact', service='dog-fact-service', span_type='web')
def dog_fact():
  dog_fact = requests.get(DOG_FACT_SERVICE).json()
  fact = dog_fact.get('facts')[0]
  app.logger.info("Important dog fact - %s" % fact)
  # set the dog fact on this span as a tag
  tracer.current_span().set_tag('dog.fact', fact)
  return fact

def extract_breed(url):
  breed = urlparse(url).path.split('/')[2]
  return breed

def image_quality(size):
  if int(size) >= 100001:
    quality = 'fantastic'
  elif int(size) in range(60000, 100000):
    time.sleep(1)
    quality = 'great'
  elif int(size) in range(30000, 60001):
    quality = 'okay'
  elif int(size) <= 30000:
    quality = 'bad'
  return quality

@app.route('/')
def home_page():
  parent_id = int(tracer.get_call_context().get_current_root_span().trace_id)
  app.logger.info(parent_id)
  tracer.set_tags({'parent_span': parent_id})
  return render_template('index.html',
            image_url=dog_image(),
            dog_fact=dog_fact()
          )

@app.route('/traffic')
def make_traffic():
  # very hacky way to generate some traffic in the background
  FNULL = open(os.devnull, 'w')
  subprocess.Popen(["ab", "-n", "50", "-c", "5", "-qdS", "http://localhost:5000/"], stdout=FNULL, stderr=subprocess.STDOUT)
  return redirect("/")


if __name__ == '__main__':
  app.run(host='0.0.0.0')