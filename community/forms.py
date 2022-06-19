from .models import Comment
from django import forms

class CommentForm(forms.ModelForm):
    content = forms.CharField(label='Content', max_length=200, widget=forms.Textarea(attrs={'rows': 5, 'cols': 5}))
    class Meta:
        model = Comment
        fields = ('content',)