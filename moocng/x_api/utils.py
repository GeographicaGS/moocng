# -*- coding: utf-8 -*-

import requests
import sys
import json

from django.conf import settings
from django.contrib.auth.models import User

from moocng.courses.models import Course

def sendStatement(verb):
	try:
		headers = {
			"Content-Type": "application/json",
			"X-Experience-API-Version": "1.0.0",
			"Authorization": "Basic MTA4NTMwZmE4NGFiMWMwYTdiZTFiNzUxNDI0NTkyOTgzNWE1YTRkMTpkNGI4Nzk4MDNlYTBlMjAzODQzZmRhODE1MmY3ODAzYWE1YTdiNjRl"
		}
		r = requests.post(settings.XAPI_URL, data=json.dumps(verb), headers=headers)
		if r.status_code == requests.codes.ok:
			print "  --> Statement sended succesfully"
		else:
			print "  --> Couldn't send this statement"
			print r.text

	except:
		print "  !!! Error sending statement"
		print "      Unexpected error:", sys.exc_info()

def learnerEnrollsInMooc(user, course):
	verb = {
		    "actor": {
		        "objectType": "Agent",
		        "account": {
            		"homePage": "https://portal.ecolearning.eu?user=%s" % (user.get_profile().sub),
            		"name": user.get_profile().sub
        		}
		    },
		    "verb": {
		        "id": "http://adlnet.gov/expapi/verbs/registered",
		        "display": {
		            "es-ES": "se ha matriculado en el MOOC",
		        },
		    },
		    "object": {
		        "objectType": "Activity",
		        "id": 'oai:' + '.'.join(settings.API_URI.split(".")[::-1]) + ":" + str(course.id),
		        "definition": {
		            "name": {
		                "es-ES": course.name,
		            },
		            "description": {
		                "es-ES": course.description,
		            },
		            "type": "http://adlnet.gov/expapi/activities/course",
		        }
		    },
	    	# "context": {
	     #    	"extensions": {
	     #        	"http://vocab.org/placetime/geopoint/latitude/": "37.35",
	     #        	"http://vocab.org/placetime/geopoint/longitude/": "-6.05"
	     #    	}
	    	# }
		}
	sendStatement(verb)

def learnerAccessAPage(user, page):
	verb = {
    	"actor": {
	        "objectType": "Agent",
	        "account": {
        		"homePage": "https://portal.ecolearning.eu?user=%s" % (user.get_profile().sub),
        		"name": user.get_profile().sub
    		}
	    },
	    "verb": {
	        "id": "http://activitystrea.ms/schema/1.0/access",
	        "display": {
	            "en-US": "Indicates the learner accessed a page"
	        }
	    },
		    "object": {
	        "objectType": "Activity",
	        "id": page['url'],
	        "definition": {
	            "name": {
	                "en-US": page['name']
	            },
	            "description": {
	                "en-US": page['description']
	            },
	            "type": "http://activitystrea.ms/schema/1.0/page"
	        }
        },
	    	# "context": {
	     #    	"extensions": {
	     #        	"http://vocab.org/placetime/geopoint/latitude/": "37.35",
	     #        	"http://vocab.org/placetime/geopoint/longitude/": "-6.05"
	     #    	}
	    	# }
	}

	sendStatement(verb)