from django import template
from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from moocng.enrollment import BaseEnrollment

class GuestListEnrollment(BaseEnrollment):

    name = 'guestlist'
    title = _(u'Guest list enrollment')

    urls = patterns(
        'moocng.guestlist_enrollment.views',
        url(
            r'^guestlist-enroll/(?P<course_slug>[-\w]+)/$',
            'guestlist_enrollment',
            name='guestlist_enrollment'
        ),
        url(
            r'^guestlist-unenroll/(?P<course_slug>[-\w]+)/$',
            'guestlist_unenrollment',
            name='guestlist_unenrollment'
        ),
    )

    def render_enrollment_button(self, context, course):
        # Check if the user can enroll or not
        from django.contrib.auth.models import User
        from moocng.guestlist_enrollment.models import CourseGuestList
        try:
            user = User.objects.get(id=context['request'].user.id)
            if user:
                on_guestlist = CourseGuestList.objects.get(course=course, email=user.email) is not None
            else:
                on_guestlist = False
        except:
            on_guestlist = False
        tpl = template.loader.get_template('guestlist_enrollment_button.html')
        context['on_guestlist'] = on_guestlist
        return tpl.render(context)

    def render_unenrollment_button(self, context, course):
        tpl = template.loader.get_template('guestlist_unenrollment_button.html')
        return tpl.render(context)

def unenroll_student(course, student):
    from moocng import mongodb
    from bson.objectid import ObjectId
    from moocng.x_api import utils as x_api

    if course.has_groups:
        groupCollection = mongodb.get_db().get_collection('groups')
        group = groupCollection.find_one( { 'id_course': course.id, 'members.id_user':student.id } )
        if(group):
            for m in group["members"]:
                if(m["id_user"] == student.id):
                    group["members"].remove(m)
                    if "size" in group:
                        group["size"] -= 1
                    else:
                        group["size"] = len(group["members"])

            groupCollection.update({'_id': ObjectId(group["_id"])}, {"$set": {"members": group["members"], "size": group["size"]}})

    course.students.through.objects.get(student=student,
                                        course=course).delete()

    geolocation = {
        'lat': 0.0,
        'lon': 0.0
    }

    x_api.learnerUnenrollsInMooc(student, course, geolocation)
