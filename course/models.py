from django.db import models
import uuid
import os
import mimetypes
from django.utils.deconstruct import deconstructible
from django.conf import settings
import os
import cv2
from io import BytesIO
from django.core.files import File
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='course-thumbnails/')
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)


@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = filename.split('.')[0]
        if instance.pk:
            return filename
        else:
            filename = '{}_{}.{}'.format(filename, uuid.uuid4().hex, ext)
        return os.path.join(self.path, filename)


class Content(models.Model):
    TEXT = 'TEXT'
    IMAGE = 'IMAGE'
    PDF = 'PDF'
    WEBPAGE = 'WEBPAGE'
    AUDIO = 'AUDIO'
    VIDEO = 'VIDEO'
    OTHER = 'OTHER'

    CONTENT_CHOICES = [
        (TEXT, 'Text'),
        (IMAGE, 'Image'),
        (PDF, 'PDF'),
        (WEBPAGE, 'Webpage'),
        (AUDIO, 'Audio'),
        (VIDEO, 'Video'),
        (OTHER, 'Other'),
    ]

    content_path = PathAndRename("contents/")

    title = models.CharField(max_length=200)
    lesson = models.ForeignKey(Lesson, related_name='contents', on_delete=models.CASCADE)
    content_type = models.CharField(
        max_length=10,
        choices=CONTENT_CHOICES,
        default=TEXT,
    )
    order = models.PositiveIntegerField(default=0)
    text_content = models.TextField(blank=True)
    image_content = models.ImageField(upload_to=content_path, blank=True)
    pdf_content = models.FileField(upload_to=content_path, blank=True)
    webpage_content = models.URLField(blank=True)
    audio_content = models.FileField(upload_to=content_path, blank=True)
    audio_type = models.CharField(max_length=100, blank=True)
    video_content = models.FileField(upload_to=content_path, blank=True)
    video_type = models.CharField(max_length=100, blank=True)
    other_content = models.FileField(upload_to=content_path, blank=True)
    viewed_by = models.ManyToManyField('user.UserModel', related_name='viewed_contents', blank=True)

    def save(self, *args, **kwargs):
        if self.audio_content:
            self.audio_type = mimetypes.guess_type(self.audio_content.name)[0]
        if self.video_content:
            self.video_type = mimetypes.guess_type(self.video_content.name)[0]
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return 'Content for lesson {}'.format(self.lesson.title)


class LessonProgress(models.Model):
    student = models.ForeignKey('user.UserModel', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)

    class Meta:
        unique_together = ['student', 'lesson']
        verbose_name_plural = 'LessonProgress'

    def __str__(self):
        return f'{self.student} progress in {self.lesson}'


class Assignment(models.Model):
    course = models.ForeignKey(Course, related_name='assignments', on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_assignments', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    creation_date = models.DateTimeField(auto_now_add=True)
    attemptsAllowed = models.PositiveIntegerField(default=1)
    is_published = models.BooleanField(default=False)


class AssignmentFile(models.Model):
    assignent_path = PathAndRename("assignments/")

    file = models.FileField(upload_to=assignent_path, null=True, blank=True)
    assignment = models.ForeignKey(Assignment, related_name='files', on_delete=models.CASCADE)


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, related_name='submissions', on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submissions', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (
        ('SUBMITTED', 'Submitted'),
        ('EVALUATED', 'Evaluated'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SUBMITTED')

    class Meta:
        ordering = ['-submission_date']


class SubmissionFile(models.Model):
    submission_path = PathAndRename("submission/")

    file = models.FileField(upload_to=submission_path, null=True, blank=True)
    submission = models.ForeignKey(AssignmentSubmission, related_name='files', on_delete=models.CASCADE)


class Quiz(models.Model):
    course = models.ForeignKey(Course, related_name='quizzes', on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_quizzes', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    attempts_allowed = models.IntegerField(default=1)
    due_date = models.DateTimeField()
    creation_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Question(models.Model):
    QUIZ_TYPES = (
        ('MCQ', 'Multiple Choice Question'),
        ('MCMS', 'Multi-Choice Multiple Selection Question'),
        ('FITB', 'Fill in the Blanks'),
        ('TF', 'True/False'),
    )
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=4, choices=QUIZ_TYPES)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='attempts', on_delete=models.CASCADE)
    answer_text = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + ' - ' + str(self.question) + ' - ' + self.answer_text


class QuizProgress(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)


class AssignmentProgress(models.Model):
    assignment = models.ForeignKey(Assignment, related_name='progress', on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    submission = models.ForeignKey(AssignmentSubmission, related_name='progress', on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('assignment', 'student')


class OtherGrade(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    class Meta:
        unique_together = ('student', 'name')

def generate_certificates(names):
    template_path = "certificate-template.jpg"
    output_folder = "generated-certificates/"
    os.makedirs(output_folder, exist_ok=True)

    for index, name in enumerate(names, start=1):
        certificate_image = cv2.imread(template_path)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 5
        font_thickness = 10
        text_color = (0, 0, 0)


        (text_width, text_height), _ = cv2.getTextSize(name, font, font_scale, font_thickness)
        position_x = int((certificate_image.shape[1] - text_width) / 2)
        position_y = int((certificate_image.shape[0] + text_height) / 2)


        cv2.putText(certificate_image, name, (position_x, position_y), font, font_scale, text_color, font_thickness,
                    cv2.LINE_AA)


        file_name = f"{name}.jpg"
        file_path = os.path.join(output_folder, file_name)
        cv2.imwrite(file_path, certificate_image)


        with open(file_path, 'rb') as file:
            certificate_file = File(file)


        certificate = Certificate(name=name, certificate=certificate_file)
        certificate.save()

        print(f"Processing {index} / {len(names)}")


        os.remove(file_path)

class Certificate(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Foreign key to link the certificate to a course
    certificate_file = models.FileField(upload_to='certificates/')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate for {self.user.username} - {self.course.name}"
