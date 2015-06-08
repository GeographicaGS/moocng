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
			"Authorization": settings.XAPI_AUTH
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

def learnerEnrollsInMooc(user, course, geolocation):
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
		    "context": {
		    	"extensions": {
		    		"http://activitystrea.ms/schema/1.0/place": {
		                "objectType": "Place",
		                "id": "http://vocab.org/placetime/geopoint/wgs84/X%sY%s.html" % (geolocation['lon'], geolocation['lat']),  # Not mandatory, Maren Scheffel asked for it
		                "geojson": {
		                    "type": "FeatureCollection",
		                    "features": [
		                        {
		                            "type": "Feature",
		                            "geometry": {
		                                "type": "Point",
		                                "coordinates": [geolocation['lon'], geolocation['lat']]
		                            },
#		                            "properties": {
#		                                "property1": "value1"  # Not mandatory, but useful to include more metadata about geolocation
#		                            }
		                        }
		                    ]
		                },
		                "definition": {
		                    "name": {
		                        "en-US": "Place"
		                    },
		                    "description": {
		                        "en-US": "Represents a physical location."
		                    },
		                    "type": "http://activitystrea.ms/schema/1.0/place"
		                }
		            }
		        }
		    }
		}
	sendStatement(verb)

def learnerAccessAPage(user, page, geolocation):
	page_type = {
		"course": "http://adlnet.gov/expapi/activities/course",
		"questionnaire": "http://adlnet.gov/expapi/activities/assessment",
		"page": "http://activitystrea.ms/schema/1.0/page",
		"module": "http://adlnet.gov/expapi/activities/module",
		"syllabus": "http://www.ecolearning.eu/expapi/activitytype/syllabus",
		"learningactivity": "http://www.ecolearning.eu/expapi/activitytype/learningactivity",
		"task": "http://activitystrea.ms/schema/1.0/task",
		"assignment": "http://id.tincanapi.com/activitytype/school-assignment",
		"assessment": "http://adlnet.gov/expapi/activities/assessment",
		"peerassessment": "http://www.ecolearning.eu/expapi/activitytype/peerassessment",
		"peerproduct": "http://www.ecolearning.eu/expapi/activitytype/peerproduct",
		"learningresource": "http://adlnet.gov/expapi/activities/media",
		"forum": "http://id.tincanapi.com/activitytype/discussion",
		"blog": "http://www.ecolearning.eu/expapi/activitytype/blog",
		"blogpage": "http://www.ecolearning.eu/expapi/activitytype/blogpage",
		"blogpost": "http://www.ecolearning.eu/expapi/activitytype/blogpage",
		"wiki": "http://www.ecolearning.eu/expapi/activitytype/wiki",
		"wikipage": "http://www.ecolearning.eu/expapi/activitytype/wiki",
		"activitystream": "http://www.ecolearning.eu/expapi/activitytype/activitystream"
	}
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
	    "context": {
	        "extensions": {
	            "http://activitystrea.ms/schema/1.0/place": {
	                "objectType": "Place",
	                "id": "http://vocab.org/placetime/geopoint/wgs84/X%fY%f.html" % (geolocation['lon'], geolocation['lat']), # Not mandatory, Maren Scheffel asked for it
	                "geojson": {
	                    "type": "FeatureCollection",
	                    "features": [
	                        {
	                            "type": "Feature",
	                            "geometry": {
	                                "type": "Point",
	                                "coordinates": [geolocation['lon'], geolocation['lat']]
	                            },
#	                            "properties": {
#	                                "property1": "value1" # Not mandatory, but useful to include more metadata about geolocation */
#	                            }
	                        }
	                    ]
	                },
	                "definition": {
	                    "name": {
	                        "en-US": "Place"
	                    },
	                    "description": {
	                        "en-US": "Represents a physical location."
	                    },
	                    "type": "http://activitystrea.ms/schema/1.0/place"
	                }
	            }
	        }
	    }
	}

	sendStatement(verb)