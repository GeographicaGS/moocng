# -*- coding: utf-8 -*-

import requests
import sys
import json
import re
import time

from django.conf import settings
from django.contrib.auth.models import User

from moocng.courses.models import Course

def sendStatement(verb):
	try:
		print "Statement: " + json.dumps(verb)
		headers = {
			"Content-Type": "application/json",
			"X-Experience-API-Version": "1.0.0",
			"Authorization": settings.XAPI_AUTH
		}
		r = requests.post(settings.XAPI_URL, data=json.dumps(verb), headers=headers)
		if not r.status_code == requests.codes.ok:
			print "  --> Couldn't send this statement"
			print r.text

	except:
		print "  !!! Error sending statement"
		print "      Unexpected error:", sys.exc_info()

def learnerEnrollsInMooc(user, course, geolocation, timestamp=None):
	if not timestamp:
		timestamp = time.gmtime()
	formatted_timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", timestamp)

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
		            "en-US": "se ha matriculado en el MOOC",
		        },
		    },
		    "object": {
		        "objectType": "Activity",
		        "id": 'oai:' + '.'.join(settings.API_URI.split(".")[::-1]) + ":" + str(course.id),
		        "definition": {
		            "name": {
		                "en-US": course.name,
		            },
		            "description": {
		                "en-US": course.description,
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
		    },
		    "timestamp": formatted_timestamp
		}
	sendStatement(verb)

def learnerAccessesMooc(user, course, geolocation, timestamp=None):
	if not timestamp:
		timestamp = time.gmtime()
	formatted_timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", timestamp)

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
		            "en-US": "Indicates the learner accessed the MOOC",
		        },
		    },
		    "object": {
		        "objectType": "Activity",
		        "id": 'oai:' + '.'.join(settings.API_URI.split(".")[::-1]) + ":" + str(course.id),
		        "definition": {
		            "name": {
		                "en-US": course.name,
		            },
		            "description": {
		                "en-US": course.description,
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
		                            }
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
		    },
		    "timestamp": formatted_timestamp
		}
	sendStatement(verb)

def learnerAccessAPage(user, page, course, geolocation, timestamp=None):
	page_types = {
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
	page_verbs = {
		"course": "Indicates the learner accessed a course",
		"questionnaire": "Indicates the learner accessed a questionnaire",
		"page": "Indicates the learner accessed a page",
		"module": "Indicates the learner accessed a module",
		"syllabus": "Indicates the learner accessed a syllabus",
		"learningactivity": "Indicates the learner accessed a learning activity",
		"task": "Indicates the learner accessed a task",
		"assignment": "Indicates the learner accessed an assignment",
		"assessment": "Indicates the learner accessed an assessment",
		"peerassessment": "Indicates the learner accessed a peer assessment",
		"peerproduct": "Indicates the learner accessed a peer product",
		"learningresource": "Indicates the learner accessed a learning resource",
		"forum": "Indicates the learner accessed a forum",
		"blog": "Indicates the learner accessed a blog",
		"blogpage": "Indicates the learner accessed a blog page",
		"blogpost": "Indicates the learner accessed a blog post",
		"wiki": "Indicates the learner accessed a wiki",
		"wikipage": "Indicates the learner accessed a wikipage",
		"activitystream": "Indicates the learner accessed an activity stream",
	}

	page_type = "page"
	if re.search('\/syllabus', page['url']):
		page_type = "syllabus"
	elif re.search('\/classroom\/', page['url']):
		page_type = "module"
		if re.search('\/classroom\/.*\/kq[0-9]+\/q', page['url']):
			page_type = "task"
		if re.search('\/classroom\/.*\/kq[0-9]+\/p', page['url']):
				page_type = "peerassessment"
		elif re.search('\/classroom\/.*\/kq[0-9]+\/a', page['url']):
			page_type = "answer"

	

	if not timestamp:
		timestamp = time.gmtime()
	formatted_timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", timestamp)

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
	            "en-US": page_verbs[page_type]
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
	            "type": page_types[page_type]
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
	        },
			"contextActivities": {
				"parent": [
					{
						"id": 'oai:' + '.'.join(settings.API_URI.split(".")[::-1]) + ":" + str(course.id),
						"objectType": "Activity",
						"definition": {
							"name": {
								"en-US": course.name
							},
							"description": {
								"en-US": course.description
							},
							"type": "http://adlnet.gov/expapi/activities/course"
						}
					}
				]
			}
		},
	    "timestamp": formatted_timestamp
	}

	sendStatement(verb)
