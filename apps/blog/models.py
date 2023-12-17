from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField
from apps.services.utils import unique_slugify

# Create your models here.

class PostManager(models.Manager):
    def all(self):
        return self.get_queryset().select_related('author', 'category').filter(status='published')


class Post(models.Model):
    STATUS_OPTIONS = (
        ('published', 'Опубликованный'),
        ('draft', 'Черновик')
    )

    title = models.CharField(verbose_name='Название записи', max_length=255)
    slug = models.SlugField(verbose_name='URL', max_length=255, blank=True)
    description = RichTextField(config_name='awesome_ckeditor', verbose_name='Краткое описание', max_length=500)
    text = RichTextField(config_name='awesome_ckeditor', verbose_name='Полный текст записи')
    category = TreeForeignKey('Category', on_delete=models.PROTECT, related_name='posts', verbose_name='Категория', null=True)
    thumbnail = models.ImageField(
        verbose_name='Изображение записи',
        blank=True,
        upload_to='images/thumbnails/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'webp', 'jpeg', 'gif'))]
    )
    
    status = models.CharField(choices=STATUS_OPTIONS, default='published',
                              verbose_name='Стаутс записи', max_length=10)
    create = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')
    updated = models.DateTimeField(auto_now=True, verbose_name='Время обнавления')
    author = models.ForeignKey(to=User, verbose_name='Автор',on_delete=models.SET_DEFAULT,
                               related_name='author_posts', default=1)
    updater = models.ForeignKey(to=User, verbose_name='Обновил', on_delete=models.SET_NULL, null=True,
                                related_name='updater_posts', blank=True)
    fixed = models.BooleanField(verbose_name='Прикреплено', default=False)
    
    objects = models.Manager()
    custom = PostManager()
    
    tags = TaggableManager()
    
    class Meta:
        db_table = 'blog_posts'
        ordering = ['-fixed', '-create']
        indexes = [
            models.Index(fields=('-fixed', '-create', 'status'))
        ]
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
    
    def save(self, *args, **kwargs):
        self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def get_sum_rating(self):
        return sum([rating.value for rating in self.ratings.all()])
    
    def __str__(self):
        return self.title


class Category(MPTTModel):
    title = models.CharField(verbose_name='Описание категории', max_length=255)
    slug = models.SlugField(verbose_name='URL категории', max_length=255, blank=True)
    description = models.TextField(verbose_name='Описание категории', max_length=300)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name='children',
        verbose_name='Родительская категория',
    )
    
    class MPTTMeta:
        order_insertion_by = ('title',)
        
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        db_table = 'app_categories'
        
    def get_absolute_url(self):
        return reverse('blog:post_by_category', kwargs={'slug': self.slug})
    
        
    def __str__(self):
        return self.title
    
    
class Comment(MPTTModel):
    STATUS_OPTIONS = (
        ('published', 'Опубликовано'),
        ('draft', 'Черновик')
    )
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Запись', related_name='comments')
    author = models.ForeignKey(User, verbose_name='Автор комментария', on_delete=models.CASCADE, related_name='commetns_author')
    content = models.TextField(verbose_name='Текст комментария', max_length=3000)
    time_create = models.DateTimeField(verbose_name='Время добавления', auto_now_add=True)
    time_update = models.DateTimeField(verbose_name='Дата обновления', auto_now=True)
    status = models.CharField(choices=STATUS_OPTIONS, default='published', verbose_name='Статус поста', max_length=10)
    parent = TreeForeignKey('self', verbose_name='Родительский комментарий', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    
    class MTTMeta:
        order_insertion_by = ('-time_create',)
        
    class Meta:
        ordering = ['-time_create']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        
    def __str__(self) -> str:
        return f'{self.author}: {self.content}'
    
    
class Rating(models.Model):
    post = models.ForeignKey(to=Post, verbose_name='Запись', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(to=User, verbose_name='Пользователь', on_delete=models.CASCADE,
                             null=True, blank=True)
    value = models.IntegerField(verbose_name='Значение', choices=[(1, 'Нравится'), (-1, 'Не нравится')])
    time_create = models.DateTimeField(verbose_name='Время добавления', auto_now_add=True)
    ip_address = models.GenericIPAddressField(verbose_name='IP Адрес')
    
    class Meta:
        unique_together = ('post', 'ip_address')
        ordering = ('-time_create',)
        indexes = [
            models.Index(fields=('-time_create', 'value'))
        ]
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'
        
        def __str__(self):
            return self.post.title