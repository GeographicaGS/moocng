from django.utils import simplejson
from django.http import HttpResponse
import datetime
import re
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from moocng.courses.models import Course, CourseTeacher
from moocng.courses.security import (get_course_progress_for_user)
from moocng.portal.templatetags.gravatar import (gravatar_for_email)
from moocng.users.models import User
from django.conf import settings
from django.utils.translation import ugettext as _


def ListRecords(request, num="1"):
	# courses = Course.objects.values("id", "name")
	courses = Course.objects.filter(status="p")
	# print(courses)
    # root = ElementTree.XML('<?xml version="1.0" encoding="ISO-8859-1"?><context><namespace><prefix>org.instantknowledge.com.</prefix><context>battery</context></namespace><data><state>86%</state><charging>false</charging></data></context>')
	
	# xml = dicttoxml.dicttoxml(to_json, attr_type=False, custom_root="OAI-PMH")
	root = Element('OAI-PMH')
	root.set('xmlns', 'http://www.openarchives.org/OAI/2.0/')
	root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
	root.set('xsi:schemaLocation', 'http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd')
	root.set('xmlns:lom', 'http://ltsc.ieee.org/xsd/LOM')
	root.set('xmlns:eco', 'http://www.ecolearning.eu/xsd/LOM')

	responseDate = SubElement(root, 'responseDate')
	responseDate.text = datetime.datetime.now().isoformat()

	request = SubElement(root, 'responseDate')
	request.set('verb', 'ListRecords')
	request.text = "http://streetlearn.appspot.com/oai"

	listRecords = SubElement(root, 'ListRecords')

	# print(settings.API_URI)
	# print(Course.objects.values("id", "name"))

	for course in courses:
		record = SubElement(listRecords, 'record')
		header = SubElement(record, 'header')
		identifier = SubElement(header, 'identifier') 
		identifier.text = '.'.join(settings.API_URI.split(".")[::-1]) + ":" + str(course.id)
		datestamp = SubElement(header, 'datestamp')   #TODO
		if course.start_date:
			datestamp.text = datetime.datetime.strptime(str(course.start_date), '%Y-%m-%d').isoformat()
		metadata = SubElement(record, 'metadata')
		lom = SubElement(metadata, 'lom:lom')
		general = SubElement(lom, 'lom:general')
		lidentifier = SubElement(general, 'lom:identifier')
		lcatalog = SubElement(lidentifier, 'lom:catalog')
		lcatalog.text = '.'.join(settings.API_URI.split(".")[::-1])
		lentry = SubElement(lidentifier, 'lom:entry')
		lentry.text=str(course.id)
		ltitle = SubElement(general, 'lom:title')
		
		if(len(course.languages.all()) == 0):
			lstring = SubElement(ltitle, 'lom:string')  
			lstring.set('language', 'null')
			lstring.text=course.name
		else:
			for language in course.languages.all():
				lstring = SubElement(ltitle, 'lom:string')  
				lstring.set('language', language.abbr)
				lstring.text=course.name
		
		if(len(course.languages.all()) == 0):
			ldescription = SubElement(general, 'lom:description')
			lstring = SubElement(ldescription, 'lom:string')  
			lstring.set('language', 'null') 
			lstring.text = re.sub('<[^<]+?>', '', course.description)

		else:
			for language in course.languages.all():
				ldescription = SubElement(general, 'lom:description')
				lstring = SubElement(ldescription, 'lom:string')  
				lstring.set('language', language.abbr) 
				lstring.text = re.sub('<[^<]+?>', '', course.description)

		if(len(course.languages.all()) == 0):
			llanguage = SubElement(general, 'lom:language')
			llanguage.text = "null"
		else:
			for language in course.languages.all():
				llanguage = SubElement(general, 'lom:language')
				llanguage.text = language.abbr

		units = course.unit_set.all()
		knowledgequantum = 0
		for unit in units:
			knowledgequantum += len(unit.knowledgequantum_set.all())

		nrOfUnits = SubElement(general, 'eco:nrOfUnits')
		nrOfUnits.text = str(knowledgequantum)

		startDate = SubElement(general, 'eco:startDate')
		if course.start_date:
			startDate.text = datetime.datetime.strptime(str(course.start_date), '%Y-%m-%d').isoformat()

		endDate = SubElement(general, 'eco:endDate')
		if course.end_date:
			endDate.text = datetime.datetime.strptime(str(course.end_date), '%Y-%m-%d').isoformat()
		technical = SubElement(lom, 'lom:technical')
		location = SubElement(technical, 'lom:location')
		location.text = "http://" + settings.API_URI + course.get_absolute_url()
		educational = SubElement(lom, 'lom:educational')
		typicalLearningTime = SubElement(educational, 'lom:typicalLearningTime')
		duration = SubElement(typicalLearningTime, 'lom:duration')#TODO
		estimated_effort = 1
		try:
			estimated_effort = int(course.estimated_effort)
		except:
			pass
		if(course.start_date and course.end_date and estimated_effort):
			diff = ((course.end_date - course.start_date).days / 7) * int(estimated_effort)
			duration.text = "P"
			years = 0
			months = 0
			days = 0
			if(diff >= 8760):
				years = iff/8760
				if(years > 0):
					duration.text += str(years) + "Y"
					diff -= years * 8760
			
			if(diff >= 720):
				months = diff/720
				duration.text += str(months) + "M"
				diff -= months * 720

			if(diff >= 24):
				days = diff/24
				duration.text += str(days) + "D"
				diff -= (days * 24)

			duration.text += "T"
			if(diff != 0):
				duration.text += str(diff) + "H"


		lifeCycle = SubElement(lom, 'lom:lifeCycle')
		
		for teacher in course.teachers.all():
			lcontribute = SubElement(lifeCycle, 'lom:contribute')
			lrole = SubElement(lcontribute, 'lom:role')
			lsource = SubElement(lrole, 'lom:source')
			lsource.text = "LOMv1.0"
			lvalue = SubElement(lrole, 'lom:value')
			lvalue.text = "author"
			lentity = SubElement(lcontribute, 'lom:entity')
			organization = "ECO"
			try:
				organization = teacher.get_profile().organization.all()[0].name
			except:
				pass
			lentity.text="<![CDATA[BEGIN:VCARD \r\nFN:" + teacher.first_name + " " + teacher.last_name + " \r\nUID:urn:uuid:" + str(teacher.id) + " \r\nEMAIL;TYPE=INTERNET:" + teacher.email + " \r\nORG:" + organization + " N:" + teacher.last_name +";" + teacher.first_name + " \r\nVERSION:3.0 \r\nEND:VCARD \r\n]]>"
		
		lclassification = SubElement(lom, 'lom:classification')
		lpurpose = SubElement(lclassification, 'lom:purpose')
		lsource = SubElement(lpurpose, 'lom:source')
		lsource.text = "LOMv1.0"
		lvalue = SubElement(lpurpose, 'lom:value')
		lvalue.text = "discipline"
		ltaxonPath = SubElement(lclassification, 'lom:taxonPath')
		lsource = SubElement(ltaxonPath, 'lom:source')
		lstring = SubElement(lsource, 'lom:string')
		request.set('language', 'en')
		lstring.text = "ECO Area of Interests"
		ltaxon = SubElement(ltaxonPath, 'lom:taxon')
		categories = course.categories.all()
		if(len(categories) > 0):
			lid = SubElement(ltaxon, 'lom:id')
			lid.text = "ECO:" + categories[0].slug
			lentry = SubElement(ltaxon, 'lom:entry')
			lstring = SubElement(lentry, 'lom:string')
			lstring.text = categories[0].name
		

	return HttpResponse(tostring(root), mimetype='application/xml')



# from django.utils import simplejson
# from django.http import HttpResponse
# from xml.etree.ElementTree import Element, SubElement, Comment, tostring

# def prueba(request):
# 	a = "awdadawd"
#    	top = Element('top')
# 	return HttpResponse(tostring(top), mimetype='application/xml')


def courses_by_users(request,id):
	result = []
	user = User.objects.get(id=id)
	for coursestudent in user.coursestudent_set.all():
		result.append({"id":str(coursestudent.course_id) , "progressPercentage" : get_course_progress_for_user(coursestudent.course, user)})

	return HttpResponse(simplejson.dumps(result), mimetype='application/json')

def teacher(request,id):
	teacher = CourseTeacher.objects.filter(teacher_id=id)[0].teacher

	return HttpResponse(simplejson.dumps([{"name":teacher.first_name + " " + teacher.last_name, "imageUrl":"http:" + gravatar_for_email(teacher.email)}]), mimetype='application/json')
	

def heartbeat(request):
    return HttpResponse(simplejson.dumps({"alive_at": datetime.datetime.now().isoformat()}), mimetype='application/json')
