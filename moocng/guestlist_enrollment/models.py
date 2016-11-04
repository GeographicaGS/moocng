from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from moocng.courses.models import Course

class CourseGuestList(models.Model):
    course = models.ForeignKey(
        Course,
        verbose_name=_(u'Course'),
        blank=False,
        null=False
    )
    student = models.ForeignKey(
        User,
        verbose_name=_(u'Student'),
        blank=True,
        null=True
    )
    email = models.EmailField(
        verbose_name=_(u'Email'),
        blank=True,
        null=True
    )
    STUDENT_STATUSES = (
        ('i', _(u'Invited')),
        ('e', _(u'Enrolled')),
        ('w', _(u'Waiting to be invited')),
    )

    status = models.CharField(
        verbose_name=_(u'Status'),
        choices=STUDENT_STATUSES,
        max_length=10,
        default=STUDENT_STATUSES[0][0],
    )

    class Meta:
        verbose_name = _(u'Course guest student')
        verbose_name_plural = _(u'Course guest students')

    def __unicode__(self):
        return u'%s - %s -> %s' % (self.course.name, self.student.username, self.status)
