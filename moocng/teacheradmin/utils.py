# -*- coding: utf-8 -*-
# Copyright 2012-2013 UNED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from django.contrib.sites.models import get_current_site
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from moocng.courses.utils import send_mail_wrapper


def send_invitation_not_registered(request, invitation):
    subject = _(u'You have been invited to be a teacher in "%s"') % invitation.course.name
    template = 'teacheradmin/email_invitation_teacher_not_registered.txt'
    context = {
        'host': invitation.host.get_full_name() or invitation.host.username,
        'course': invitation.course.name,
        'course_url': "https://%s%s" % (request.get_host(), reverse('course_overview', args=[invitation.course.slug])),
        'site': get_current_site(request).name
    }
    to = [invitation.email]
    send_mail_wrapper(subject, template, context, to)

def send_invitation_registered(request, email, course):
    subject = _(u'You have been invited to be a teacher in "%s"') % course.name
    template = 'teacheradmin/email_invitation_teacher.txt'
    context = {
        'course': course.name,
        'host': request.user.get_full_name() or request.user.username,
        'course_url': "https://%s%s" % (request.get_host(), reverse('course_overview', args=[course.slug])),
        'site': get_current_site(request).name
    }
    to = [email]
    send_mail_wrapper(subject, template, context, to)

def send_removed_notification(request, email, course):
    subject = _(u'You have been removed as teacher from "%s"') % course.name
    template = 'teacheradmin/email_remove_teacher.txt'
    context = {
        'course': course.name,
        'host': request.user.get_full_name() or request.user.username,
        'site': get_current_site(request).name
    }
    to = [email]
    send_mail_wrapper(subject, template, context, to)
