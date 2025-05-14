from django import forms
from django.core.validators import FileExtensionValidator
from django.forms import ClearableFileInput, FileInput
from .models import Book, Collection, Comments, BookImage
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# Custom field for handling multiple files
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        widget = MultipleFileInput(attrs={
            'multiple': True,
            'class': 'form-control-file',
            'accept': 'image/jpeg,image/png',
        })
        kwargs.setdefault("widget", widget)
        kwargs.setdefault(
            'validators',
            [FileExtensionValidator(allowed_extensions=['jpg','jpeg','png'])]
        )
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class BooksForm(forms.ModelForm):
    additional_images = MultipleFileField(
        required=False,
    )

    class Meta:
        model = Book
        fields = ['title', 'isbn', 'author', 'status', 'condition', 'genre', 'location', 'description', 'cover_image', 'additional_images']

    def __init__(self, *args, **kwargs):
        super(BooksForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter title'})
        self.fields['author'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter author'})
        self.fields['isbn'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter isbn'})
        self.fields['status'].widget.attrs.update({'class': 'form-select', 'placeholder': 'Select status'})
        self.fields['status'].choices = Book.Status.choices
        self.fields['condition'].widget.attrs.update({'class': 'form-select', 'placeholder': 'Select condition'})
        self.fields['condition'].choices = Book.Condition.choices
        self.fields['genre'].widget.attrs.update({'class': 'form-select', 'placeholder': 'Select genre'})
        self.fields['genre'].choices = Book.Genre.choices
        self.fields['location'].widget.attrs.update({'class': 'form-select', 'placeholder': 'Select location'})
        self.fields['location'].choices = Book.Location.choices
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Provide description'})
        self.fields['cover_image'].widget.attrs.update({'class': 'form-control-file', 'required': 'required'})

        for field_name, field in self.fields.items():
            if field_name not in ['additional_images']:
                field.required = True

        # but if we're editing (instance exists in DB), make cover_image optional
        if self.instance and self.instance.pk:
            cover = self.fields['cover_image']
            cover.required = False
            # also remove the HTML "required" attribute so client-side won't complain
            cover.widget.attrs.pop('required', None)
            # replace the ClearableFileInput with a plain FileInput
            cover.widget = FileInput(
                attrs={'class': 'form-control-file'}
            )

class CommentsForm(forms.ModelForm):
    rating = forms.ChoiceField(choices=[('', 'Select a rating')]+ [(str(i), str(i)) for i in range(1, 6)], widget=forms.RadioSelect, required = True, error_messages={'required':'Please select a rating'})
    class Meta:
        model = Comments
        fields = ['comment', 'rating']
    def __init__(self, *args, **kwargs):
        super(CommentsForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter comment'})

        # Make all fields required
        for field_name, field in self.fields.items():
            field.required = True
        self.fields['rating'].empty_label = None


class AddBooksToCollectionForm(forms.ModelForm):
    books = forms.ModelMultipleChoiceField(queryset=Book.objects.none(), widget=forms.CheckboxSelectMultiple, required = False)

    class Meta:
        model = Collection
        fields = ['books']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if instance:
            # Include non-private books AND books in the current collection
            self.fields['books'].queryset = Book.objects.filter(
                Q(is_private=False) | Q(collections=instance)
            ).distinct()

class BookImageForm(forms.ModelForm):
    class Meta:
        model = BookImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image caption (optional)'})
        }

    def save(self, commit=True):
        # Handle deleting old cover image if it's being replaced
        if self.instance.pk:
            old_instance = Book.objects.get(pk=self.instance.pk)
            if old_instance.cover_image and self.cleaned_data.get('cover_image') != old_instance.cover_image:
                old_instance.cover_image.delete(save=False)
        
        return super().save(commit)

class CreateCollectionForm(forms.ModelForm):
    cover_image = forms.ImageField(
        required=True,
        error_messages={'required': 'Please upload a cover image.'},
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'placeholder': 'Upload a Cover Image',
            'required': 'required',
        })
    )
    books = forms.ModelMultipleChoiceField(
        queryset=Book.objects.filter(is_private=False),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False,
    )

    collection_type = forms.ChoiceField(
        choices=[('public', 'Public'), ('private', 'Private')],
        widget=forms.RadioSelect,
        required=True
    )
    allowed_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False,
        label="Select users who can access this collection"
    )
    
    class Meta:
        model = Collection
        fields = ['title', 'description', 'books', 'cover_image', 'collection_type', 'allowed_users']
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and self.request.user.is_authenticated:
            user = self.request.user
            if not user.userprofile.is_librarian():
                self.fields['collection_type'].choices = [('public', 'Public')]
            # Exclude current user from allowed_users list since they're already the creator, also other librarians
            self.fields['allowed_users'].queryset = User.objects.exclude(
                Q(id=user.id) | Q(userprofile__role='librarian')
            )
            self.fields['cover_image'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Upload a Cover Image'})
            # Nicely render all form fields
            for field_name, field in self.fields.items():
                if not isinstance(field.widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
                    field.widget.attrs.update({'class': 'form-control'})
                    
    def clean_cover_image(self):
        img = self.cleaned_data.get('cover_image')
        if not img:
            raise forms.ValidationError("Please upload a cover image.")
        return img
        
    def save(self, commit=True):
        if not self.request or not self.request.user.is_authenticated:
            raise ValidationError("A logged-in user is required to create a collection.")
            
        user = self.request.user
        collection_type = self.cleaned_data.get('collection_type')
        is_private = (collection_type == 'private')

        instance = super().save(commit=False)
        instance.creator = user
        instance.is_private = is_private
        
        if commit:
            instance.save()
            self.save_m2m()


        # Handle allowed users if the collection is private
            if is_private:
                allowed_users = self.cleaned_data.get('allowed_users')
                if allowed_users:
                    instance.allowed_users.set(allowed_users)
            
            # Handle books
            selected_books = self.cleaned_data.get('books')
            if selected_books:
                # First save the collection to establish its ID
                if is_private:
                    # For private collections, handle the special logic
                    for book in selected_books:
                        # Remove the book from all collections
                        book.collections.clear()
                        # Add it to this private collection
                        book.collections.add(instance)
                        # Set the book as private
                        book.is_private = True
                        book.save()
                else:
                    # For public collections, simply add books to collection
                    instance.books.set(selected_books)
                    
        return instance

class EditCollectionForm(forms.ModelForm):
    cover_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'placeholder': 'Upload a Cover Image',
        })
    )


    books = forms.ModelMultipleChoiceField(
        queryset=Book.objects.filter(is_private=False),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False,
    )
    
    allowed_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False,
        label="Select users who can access this collection"
    )

    class Meta:
        model = Collection
        fields = ['title', 'description', 'books', 'cover_image', 'allowed_users']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  
        super().__init__(*args, **kwargs)

        if self.request and self.request.user.is_authenticated:
            user = self.request.user

            # Exclude current user and librarians from allowed_users
            self.fields['allowed_users'].queryset = User.objects.exclude(
                Q(id=user.id) | Q(userprofile__role='librarian')
            )
        
        # Set common widget styling
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
                field.widget.attrs.update({'class': 'form-control'})

    def clean_cover_image(self):
        # Simply return the image or None — no validation error if it's missing
        return self.cleaned_data.get('cover_image')

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Don't update collection_type; just retain existing value
        instance.is_private = self.instance.is_private

        if commit:
            instance.save()
            self.save_m2m()

            if instance.is_private:
                instance.allowed_users.set(self.cleaned_data['allowed_users'])
            else:
                instance.allowed_users.clear()

        return instance


