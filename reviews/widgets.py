from django.forms import CheckboxInput
from django.contrib.staticfiles.storage import staticfiles_storage

class ToggleWidget(CheckboxInput):
    class Media:
        css = {'all': (
            staticfiles_storage.url("css/bootstrap-toggle.min.css"), )}
        js = (staticfiles_storage.url("js/bootstrap-toggle.min.js"),)

    def __init__(self, attrs=None, *args, **kwargs):
        attrs = attrs or {}
        
        default_options = {
            'toggle': 'toggle',
            'offstyle': 'danger',
        }
        options = kwargs.get('options', {})
        default_options.update(options)
        for key, val in default_options.items():
            attrs['data-' + key] = val

        super().__init__(attrs)



