import logging
try:
    import astropy.io.fits as fits
except ImportError:
    import pyfits as fits

import wand.image as image
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


log = logging.getLogger(__name__)

class ResourceMetadata(plugins.SingletonPlugin):
    plugins.implements(plugins.IResourceUpload)
    plugins.implements(plugins.IResourcePreview)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes)

    def before_map(self, map):
        return map

    def after_map(self, map):
        fits_preview_controller = 'ckanext.resourcemetadata.controllers:FitsPreview'
        map.connect('/dataset/{id}/resource/{resource_id}/fitspreview',
                    controller=fits_preview_controller,
                    action='fitspreview')
        return map

    def after_upload(self, context, pkg_dict, resource_id, file_path):
        log.debug('this is after upload calling')

        additional_metadata = self.get_metadata(file_path)

        for n, p in enumerate(pkg_dict['resources']):
            if p.get('id') == resource_id:
                break
        else:
            n = -1
            pkg_dict['resources'][n]['id'] = resource_id

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

        #fits_keywords = ('SIMPLE', 'BITPIX', 'NAXIS')
        #metadata = [dict((keyword, header[keyword]) 
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

    def can_preview(self, data_dict):
        format = data_dict['resource']['format']
        return format.lower() in set(['fits', 'fts', 'fit'])

    def setup_template_variables(self, context, data_dict):
        #fits_preview_controller = 'ckanext.resourcemetadata.controllers:FitsPreview'
        #preview_url = toolkit.url_for(controller=fits_preview_controller,
        #        action='fitspreview', resource_id=data_dict['resource']['id']) 
        preview_url = '/dataset/{0}/resource/{1}/fitspreview'.format(data_dict['package']['id'], data_dict['resource']['id'])
        toolkit.c.resource['preview_url'] = preview_url

    def update_config(self, config):
        toolkit.add_template_directory(config, 'theme/templates')

    def preview_template(self, context, data_dict):
       return 'fits.html' 
