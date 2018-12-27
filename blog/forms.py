from django import forms
from django.utils.translation import ugettext_lazy as _

#import re,base64

from blog.models import Comment,Article,Image,Signature
class Add_Comment(forms.ModelForm):              #alternative to RenewBookForm

    class Meta:
        model = Comment
        fields = ['name','email_address','writeup']
        labels = {'writeup': _('Comment')}
        #help_texts = {'email_address': _('Not for publication on web')}

class Compose_Form(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['title','writeup']
        labels = {'writeup': _('Narrative')}

class Image_Form(forms.ModelForm):

    class Meta:
        model = Image
        fields = ['article','img_file','caption']
        labels = {'img_file': _('Image')}

"""
class Signature_Form(forms.ModelForm):
    def save_image(self):
        dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
        signature_image = self.cleaned_data['signature_image']
        signature_image = dataUrlPattern.match(signature_image).group(2)
        signature_image = signature_image.encode()
        signature_image = base64.b64decode(signature_image)

        with open('signature.png', 'wb') as f:
            f.write(signature_image)

    class Meta:
        model = Signature
        fields = ['signature_image','signature_owner']
"""