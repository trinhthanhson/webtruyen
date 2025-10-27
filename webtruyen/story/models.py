from django.db import models

# Create your models here.

class Story(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=50)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='thumbnails/',null=True, blank=True)
    def __str__(self):
        return self.title
class Chapter(models.Model):
    story = models.ForeignKey(Story,on_delete=models.CASCADE,related_name='chapters')
    number = models.IntegerField()
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return f"{self.story.title} - Chương {self.number}"
    