#from apiclient.discovery import build
#
#client_secrets = 'client_secrets.json'
#
#service = build('')

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import argparse
import pprint
import httplib2
import urllib.request
import json
import webcolors
import requests


# [START pretty printer]
pp = pprint.PrettyPrinter(indent=4)
def printer(stuff):
    return pp.pprint(stuff)
# [END pretty printer]

# [START get_vision_service]
DISCOVERY_URL='https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'

def get_vision_service():
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('vision', 'v1', credentials=credentials,
                            discoveryServiceUrl=DISCOVERY_URL)
# [END get_vision_service]


# [START identify_image]
def identify_image(gcs_uri, max_results=50):
    """Uses the Vision API to identify the given image

    Args:
        gcs_uri: A uri of the form: gs://bucket/object

    Returns:
        An array of dicts with information about the picture..
    """
    batch_request = [{
        'image': {
            'source': {
                'gcs_image_uri': gcs_uri
            }
        },
        'features': [{
            'type': 'LABEL_DETECTION',
            'maxResults': max_results,
        },{
            'type': 'IMAGE_PROPERTIES',
            'maxResults': max_results,
        }]
    }]

    service = get_vision_service()
    request = service.images().annotate(body={
        'requests': batch_request,
        })
    response = request.execute()

    return_object = {
        'meta': response['responses'][0].get('labelAnnotations'),
        'colors': response['responses'][0].get('imagePropertiesAnnotation').get('dominantColors').get('colors'),
    }
    return return_object
# [END identify_image]


# [START determine closest color]
def closest_color(requested_color):
    min_colors = {}
    for key, name in webcolors.css3_hex_to_names.items():
        rc, gc, bc = webcolors.hex_to_rgb(key)
        rd = (rc - requested_color[0]) ** 2
        gd = (gc - requested_color[1]) ** 2
        bd = (bc - requested_color[2]) ** 2
        min_colors[(rd+gd+bd)] = name
    return min_colors[min(min_colors.keys())]
# [END determine closest color]


# [START determine color]
def get_color_name(requested_color):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_color)
    except ValueError:
        closest_name = closest_color(requested_color)
        actual_name = None
    return actual_name, closest_name
# [END determine color]


# [START drop_payload]
def drop_payload(payload):
    url = 'http://script.google.com/macros/s/AKfycbxMsw8uypjUeuBV8-75YiMlonNJIZQl-tkPe0BT6uIUIMhm3tCV/exec'
    requests.get(url, params=payload)
    return
# [END drop_payload]


# [START main]
def run(gcs_uri):
    if gcs_uri[:5] != 'gs://':
        raise Exception('Image uri must be of the form gs://bucket/object')
    identity_objects = identify_image(gcs_uri)
    colors = identity_objects['colors']
    meta = identity_objects['meta']
    if not colors:
        print(colors)
    else:
        for color_obj in colors:
            color = color_obj.get('color')
            pixel_fraction = color_obj.get('pixelFraction')
            red = color.get('red')
            green = color.get('green')
            blue = color.get('blue')
            required_colors = (red, green, blue)
            actual_name, closest_name = get_color_name(required_colors)
            if 'yellow' in closest_name or 'gold' in closest_name:
                message = gcs_uri + ' is DED'
                status = 'mildew infection'
                treatment = 'fumigate'
                result = 'pending'
                break
            elif 'green' in closest_name:
                message = gcs_uri + ' looks healthy to me ¯\_(ツ)_/¯'
                status = 'healthy'
                treatment = 'n/a'
                result = 'n/a'

        return_obj = {
                'url': gcs_uri,
                'status': status,
                'treatment': treatment,
                'result': result,
                'coordinates': '40.7053° N, 74.0140° W',
                'meta': meta,
                'message': message,
                }

        drop_payload(return_obj)

        return

# [END main]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Identifies the given image.')
    parser.add_argument(
            'gcs_uri', help=('The google Cloud Storage uri to the image to identify'
                ', of the form: gs://bucket_Name/object_name.jpg'))
    args = parser.parse_args()

    run(args.gcs_uri)
