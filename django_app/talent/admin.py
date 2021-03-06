from django.contrib import admin
from django.contrib.admin import AllValuesFieldListFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter

from talent.models import Reply
from talent.models import Review, Location, Talent, ClassImage, Registration, WishList, Curriculum, Question


class CustomDropdownFilter(AllValuesFieldListFilter):
    template = 'admin/dropdown_filter.html'


class LocationInline(admin.TabularInline):
    model = Location


class CurriculumInline(admin.TabularInline):
    model = Curriculum


class ClassImageInline(admin.TabularInline):
    model = ClassImage


class RegistrationInline(admin.TabularInline):
    model = Registration


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'student_name',
                    'title',
                    'location',
                    'joined_date',
                    'is_verified',
                    'student_level',
                    'experience_length',)
    list_filter = (('student', RelatedDropdownFilter),
                   ('talent_location__region', CustomDropdownFilter),
                   ('talent_location__talent', RelatedDropdownFilter))
    list_display_links = list_display

    def student_name(self, registration):
        return registration.student.name

    student_name.short_description = 'student'

    def location(self, registration):
        return registration.talent_location.get_region_display()

    def title(self, registration):
        return registration.talent_location.talent.title


class CurriculumAdmin(admin.ModelAdmin):
    list_display = ('pk', 'information', 'image', 'talent', 'tutor')
    list_filter = (('talent', RelatedDropdownFilter),)
    list_display_links = list_display

    def tutor(self, curriculum):
        return curriculum.talent.tutor.user.name


class ClassImageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'image', 'talent', 'tutor',)
    list_filter = (('talent', RelatedDropdownFilter),)
    list_display_links = list_display

    def talent(self, classimage):
        return classimage.talent.title

    def tutor(self, classimage):
        return classimage.talent.tutor.user.name


class TalentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'category', 'location', 'tutor', 'students_list',)
    list_filter = (
        ('category', DropdownFilter),
        ('tutor', RelatedDropdownFilter),
    )
    inlines = [LocationInline, ClassImageInline, CurriculumInline, ]
    list_display_links = list_display

    def students_list(self, talent):
        student_list = []
        for student in talent.locations.values_list('registered_student', flat=True):
            student_list.append(student)
        return student_list

    def location(self, talent):
        location_list = []
        for location in Location.objects.filter(talent=talent):
            location_list.append(location.get_region_display())
        return location_list


class LocationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'region', 'day', 'talent', 'registered_count')
    list_filter = (('talent', RelatedDropdownFilter),
                   ('day', CustomDropdownFilter),
                   ('region', CustomDropdownFilter)
                   )
    list_display_links = list_display

    inlines = [RegistrationInline, ]

    def talent(self, location):
        return location.talent.title

    def registered_count(self, location):
        return Registration.objects.filter(talent_location=location).count()


        # def registered_students(self, location):
        # for registrations in Registration.objects.filter(talent_location=location):
        #     student.append(registrations.student)
        # return student


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'comment_summary', 'talent', 'user_name', 'created_date',)
    list_filter = (
        ('talent', RelatedDropdownFilter),
        ('user', RelatedDropdownFilter),
    )
    list_display_links = list_display

    def user_name(self, review):
        return review.user.name

    user_name.short_description = 'user'


class WishAdmin(admin.ModelAdmin):
    list_display = ('pk', 'talent', 'user_name', 'added_date')
    list_filter = (('talent', RelatedDropdownFilter),)
    list_display_links = list_display

    def user_name(self, wishlist):
        return wishlist.user.name

    user_name.short_description = 'user'


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'content_summary', 'author', 'talent', 'created_date')
    list_filter = (('talent', RelatedDropdownFilter),
                   ('user', RelatedDropdownFilter))
    list_display_links = list_display

    def author(self, obj):
        return obj.user


class ReplyAdmin(admin.ModelAdmin):
    list_display = ('pk', 'content_summary', 'author', 'question_content', 'talent', 'created_date')
    list_filter = (('question__talent', RelatedDropdownFilter),)
    list_display_links = list_display

    def author(self, obj):
        return obj.tutor.user

    def question_content(self, obj):
        return obj.question.content_summary()

    def talent(self, obj):
        return obj.question.talent.title


admin.site.register(Location, LocationAdmin)
admin.site.register(Talent, TalentAdmin)
admin.site.register(ClassImage, ClassImageAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(WishList, WishAdmin)
admin.site.register(Curriculum, CurriculumAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Reply, ReplyAdmin)
