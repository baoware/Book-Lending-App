from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import UserProfile
from catalog.models import Collection, Book


class CollectionsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a dummy creator for collections.
        self.creator = User.objects.create_user(
            username="creator", password="testpass", email="creator@example.com"
        )
        # Use the auto-created profile; no manual creation.
        self.public_collection = Collection.objects.create(
            title="Public Collection",
            description="A public collection",
            is_private=False,
            creator=self.creator,
        )
        self.private_collection = Collection.objects.create(
            title="Private Collection",
            description="A private collection",
            is_private=True,
            creator=self.creator,
        )

    def test_anonymous_user_sees_only_public_collections(self):
        response = self.client.get(reverse('catalog:collections'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("Public Collection", content)
        self.assertNotIn("Private Collection", content)

    def test_authenticated_patron_does_notsee_private_collection_as_text(self):
        # Create a patron; update its auto-created profile.
        patron_user = User.objects.create_user(
            username="patron", password="testpass", email="patron@example.com"
        )
        patron_profile = patron_user.userprofile
        patron_profile.role = "patron"
        patron_profile.full_name = "Test Patron"
        patron_profile.save()

        self.client.login(username="patron", password="testpass")
        response = self.client.get(reverse('catalog:collections'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        # Expect that patrons see private collections with a "(Private)" label.
        self.assertNotIn("Private Collection", content)
        self.client.logout()

    def test_librarian_sees_private_collection_as_link(self):
        # Create a librarian user; update its auto-created profile.
        librarian_user = User.objects.create_user(
            username="librarian", password="testpass", email="librarian@example.com"
        )
        librarian_profile = librarian_user.userprofile
        librarian_profile.role = "librarian"
        librarian_profile.full_name = "Test Librarian"
        librarian_profile.save()

        self.client.login(username="librarian", password="testpass")
        response = self.client.get(reverse('catalog:collections'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        # Librarians should see private collection titles without the "(Private)" label.
        self.assertIn("Private Collection", content)
        self.assertNotIn("Private Collection (Private)", content)
        self.client.logout()





class CatalogBasicTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create two books.
        self.book1 = Book.objects.create(
            title="Django Basics",
            author="Author A",
            lender=None,
            status="Available",
            condition="Acceptable",
            genre="Romance",
            rating=3,
            location="Shannon Library",
            description="Learn Django."
        )
        self.book2 = Book.objects.create(
            title="Advanced Django",
            author="Author B",
            lender=None,
            status="Checked out",
            condition="Good",
            genre="Adventure",
            rating=4,
            location="Shannon Library",
            description="Deep dive into Django."
        )
        # Assign dummy images to both books.
        dummy_image = SimpleUploadedFile("dummy.jpg", b"dummycontent", content_type="image/jpeg")
        self.book1.cover_image = dummy_image
        self.book1.save()
        self.book2.cover_image = dummy_image
        self.book2.save()

    def test_item_view(self):
        url = reverse('catalog:item', kwargs={'book_id': self.book1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Basics")

    def test_search_view(self):
        url = reverse('catalog:search')
        response = self.client.get(url, {'query': 'Django'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("Django Basics", content)
        self.assertIn("Advanced Django", content)
        response = self.client.get(url, {'query': 'Advanced'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("Advanced Django", content)
        self.assertNotIn("Django Basics", content)


class UsersBasicTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="test@example.com"
        )
        # Update the auto-created UserProfile rather than creating a new one.
        user_profile = self.user.userprofile
        user_profile.role = "patron"
        user_profile.full_name = "Test User"
        user_profile.save()

    def test_dashboard_anonymous(self):
        response = self.client.get(reverse('users:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_authenticated(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('users:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_profile_authenticated(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
