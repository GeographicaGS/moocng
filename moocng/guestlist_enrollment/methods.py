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
                on_guestlist = CourseGuestList.objects.get(course=course, student=user) is not None
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
