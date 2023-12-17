from django import forms
from .models import Post, Comment


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'slug', 'category', 'description', 'text', 'thumbnail', 'status')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })
            

class PostUpdateForm(PostCreateForm):
    class Meta:
        model = Post
        fields = PostCreateForm.Meta.fields + ('updater', 'fixed')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['fixed'].widget.attrs.update({
            'class': 'form-check-input'
        })
        
        
class CommentCreateForm(forms.ModelForm):
    parent = forms.IntegerField(widget=forms.HiddenInput, required=False)
    content = forms.CharField(label='', widget=forms.Textarea(
        attrs={
            'cols': 30,
            'rows': 5,
            'placeholder': 'Комментарий',
            'class': 'form-control'
        }
    ))
    
    class Meta:
        model = Comment
        fields = ('content',)