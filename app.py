import logging
# set up the datadog tracer https://docs.datadoghq.com/tracing/setup/python/
from ddtrace import patch_all, tracer
import ddtrace

log = logging.getLogger()
log.level = logging.INFO

patch_all(logging=True)

from flask import Flask, render_template
import requests
from urlparse import urlparse
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
  dog_image = requests.get(DOG_IMAGE_SERVICE).json()
  image_url = dog_image.get('message')
  # find out how big the image is
  size = requests.get(image_url, stream=True).headers['Content-length']
  app.logger.info("File size of image %s" % size)
  breed = extract_breed(image_url)
  # set the breed at the root span to create a facet on
  root_span = tracer.get_call_context().get_current_root_span()
  root_span.set_tag('breed', breed)
  # set the url as a tag on this span
  tracer.current_span().set_tag('dog.image', image_url)
  if breed in GOOD_BOYS:
    root_span.set_tag('good_boy', 'true')
    app.logger.info("Very very good boye - breed=%s" % breed)
  else:
    app.logger.info("Still a good boye - breed=%s" % breed)
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

@app.route('/')
def home_page():
    patch_all(logging=True)
    return render_template('index.html',
              image_url=dog_image(),
              dog_fact=dog_fact()
            )


if __name__ == '__main__':
    app.run(host='0.0.0.0')