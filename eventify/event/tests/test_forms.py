from django.test import SimpleTestCase

from event.forms import UploadFileForm


class TestForms(SimpleTestCase):
    def test_upload_file_form_valid_data(self):
        form_data = {'something'}
        form = UploadFileForm(data=form_data)
        self.assertTrue(form.is_valid())
