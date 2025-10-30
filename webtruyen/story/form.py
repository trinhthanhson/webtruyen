from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm CSS cho Tailwind
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-dark-border bg-gray-700 text-white rounded-lg focus:ring-primary focus:border-primary transition duration-200 placeholder-gray-500'
            })