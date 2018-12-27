from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    category_label = models.CharField(max_length=30)
    description = models.CharField(max_length=50)

    def __str__(self):
        return self.category_label

class Article(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=50)
    contributor_author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    writeup = models.TextField(null=True)
    pub_date = models.DateTimeField(null=True)
    display = models.BooleanField(null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-pub_date']

class ItemCounter(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    datestr = models.CharField(max_length=20)
    counts = models.IntegerField(default=0)

    def __str__(self):
        return str(self.datestr)

class WebCounter(models.Model):
    datestr = models.CharField(max_length=20)
    counts = models.IntegerField(default=0)

    def __str__(self):
        return str(self.datestr)

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)    
    name = models.CharField(max_length=20)          #store as str(name+post_time)
    email_address = models.EmailField()     #required=False
    writeup = models.CharField(max_length=200)
    post_time = models.DateTimeField()

    def __str__(self):
        return str(str(self.name)+'|'+str(self.post_time))

    class Meta:
        ordering = ['-post_time']

class Image(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)    
    caption = models.CharField(max_length=50)
    img_file = models.ImageField(upload_to='', null=True, verbose_name='')
    display = models.BooleanField(null=True)    

    def __str__(self):
        return str(str(self.article.title)+'_'+str(self.caption)+':'+str(self.img_file))

    class Meta:
        ordering = ['caption']

class Signature(models.Model):
    signature_image = models.ImageField(upload_to='', null=True, verbose_name='')
    signature_owner = models.CharField(max_length=50)

    def __str__(self):
        return str('s_'+str(self.signature_owner))