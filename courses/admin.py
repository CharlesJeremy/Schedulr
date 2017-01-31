from django.contrib import admin, messages
from django.contrib.admin.widgets import AdminTextInputWidget
from django.db import transaction
from django.shortcuts import redirect, render

from admin_views.admin import AdminViews
import nested_admin

from .models import Course, Section, Schedule
from .scraper import extract_courses
from .utils import Quarter, DaysOfWeek


class ScheduleInline(nested_admin.NestedTabularInline):
    model = Schedule

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'days_of_week':
            kwargs['widget'] = AdminTextInputWidget()
            return db_field.formfield(**kwargs)
        return super(ScheduleInline, self).formfield_for_dbfield(db_field, request, **kwargs)


class SectionInline(nested_admin.NestedStackedInline):
    model = Section
    extra = 0
    inlines = (
            ScheduleInline,
    )


class CourseAdmin(nested_admin.NestedModelAdminMixin, AdminViews):
    """ Custom admin with link for refreshing course schedule cache. """
    admin_views = (
            ('Refresh Course Schedules', 'refresh_course_schedules'),
    )

    inlines = (
            SectionInline,
    )

    search_fields = ('subject', 'code')

    @transaction.atomic
    def refresh_course_schedules(self, request, *args, **kwargs):
        """
        Clears old course schedules and re-imports them from ExploreCourses.
        """
        if request.POST:
            Course.objects.all().delete()
            Section.objects.all().delete()
            Schedule.objects.all().delete()

            # fresh_courses = []
            # fresh_sections = []
            # fresh_schedules = []
            for c in extract_courses():
                course = Course.objects.create(subject=c.subject, code=c.code, title=c.title)
                # fresh_courses.append(course)
                for s in c.sections:
                    section = Section.objects.create(course=course, class_id=s.class_id,
                            term_year=s.term.year, term_quarter=Quarter.parse(s.term.quarter),
                            section_number=s.section_number, component=s.component,
                            instructors=s.instructors)
                    # fresh_sections.append(section)

                    sc = s.schedule
                    if sc:
                        Schedule.objects.create(section=section, start_date=sc.start_date,
                                end_date=sc.end_date,
                                days_of_week=DaysOfWeek(sc.days_of_week),
                                start_time=sc.start_time, end_time=sc.end_time,
                                location=sc.location)
                        # fresh_schedules.append(schedule)

            # TODO(zhangwen): bulk doesn't work yet.
            '''
            Course.objects.bulk_create(fresh_courses)
            Section.objects.bulk_create(fresh_sections)
            Schedule.objects.bulk_create(fresh_schedules)
            '''

            messages.success(request, "Successfully refreshed course schedules")
            return redirect('admin:index')
        else:
            opts = self.model._meta
            context = self.admin_site.each_context(request)
            context.update({
                'title': 'Refresh Course Schedules',
                'opts': opts,
            })
            return render(request, 'courses/refresh.html', context=context)


admin.site.register(Course, CourseAdmin)

