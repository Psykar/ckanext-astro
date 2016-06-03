import logging

from ckan.lib.uploader import ResourceUpload

try:
    import astropy.io.fits as fits
except ImportError:
    import pyfits as fits

import wand.image as image
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


log = logging.getLogger(__name__)


class Uploader(ResourceUpload):
    def __init__(self, resource):
        super(Uploader, self).__init__(resource)


    def upload(self, id, **kwargs):
        super(Uploader, self).upload(id, **kwargs)
        log.debug('this is after upload calling')

        file_path = self.get_path(id)

        additional_metadata = self.get_metadata(file_path)

        pkg_dict['resources'][n].update(additional_metadata)
        pkg_dict['resources'][n]['format'] = 'fits'

        self.generate_preview(file_path)

        context['model'].repo.session.rollback()
        context['defer_commit'] = True
        toolkit.get_action('package_update')(context, pkg_dict)
        context.pop('defer_commit')


    def get_metadata(self, file_path):
        hdulist = fits.open(file_path, memmap=True)
        header = hdulist[0].header

        # fits_keywords = ('SIMPLE', 'BITPIX', 'NAXIS')
        # metadata = [dict((keyword, header[keyword])
        #    for keyword in fits_keywords)]

        res_meta = {}
        for k, v in header.items():
            if k != '':
                res_meta[k] = v

        hdulist.close()
        return res_meta

    def generate_preview(self, file_path):
        img = image.Image(filename=file_path)
        preview = img.convert('jpeg')
        preview.normalize()
        preview.resize(width=879)
        preview.save(filename=file_path + '.jpg')


class ResourceMetadata(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceView)

    # IConfigurer
    def update_config(self, config):
        toolkit.add_template_directory(config, 'theme/templates')

    # IResourceView

    def can_view(self, data_dict):
        format = data_dict['resource']['format']
        return format.lower() in set(['fits', 'fts', 'fit'])

    def setup_template_variables(self, context, data_dict):
        #fits_preview_controller = 'ckanext.resourcemetadata.controllers:FitsPreview'
        #preview_url = toolkit.url_for(controller=fits_preview_controller,
        #        action='fitspreview', resource_id=data_dict['resource']['id']) 
        preview_url = '/dataset/{0}/resource/{1}/fitspreview'.format(data_dict['package']['id'], data_dict['resource']['id'])
        toolkit.c.resource['preview_url'] = preview_url




    def view_template(self, context, data_dict):
        return 'fits.html'

    def info(self):
        return {
            'name': 'fits_view',
            'title': toolkit._('FITS View'),
            'iframed': False,
            'preview_enabled': True,
            # 'schema': {
            #     'meta_data': []
            # }
        }


