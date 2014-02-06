import logging
import astropy.io.fits as fits
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
        pkg_dict['resources'][-1]['id'] = resource_id
        pkg_dict['resources'][-1].update(additional_metadata)
        pkg_dict['resources'][-1]['format'] = 'fits'

        self.generate_preview(file_path, pkg_dict)

        context['defer_commit'] = True
        toolkit.get_action('package_update')(context, pkg_dict)
        context.pop('defer_commit')



    def get_metadata(self, file_path):
        fits_keywords = ('SIMPLE', 'BITPIX', 'NAXIS')
        hdulist = fits.open(file_path, memmap=True)
        header = hdulist[0].header

        metadata = [dict((keyword, header[keyword]) 
            for keyword in fits_keywords)]

        res_meta = {}
        for k, v in header.items():
            if k != '':
                res_meta[k] = v

        hdulist.close()
        return res_meta

    def generate_preview(self, file_path, pkg_dict):
        img = image.Image(filename=file_path)
        preview = img.convert('jpeg')
        preview.normalize()
        preview.resize(width=879)
        preview.save(filename=file_path + '.jpg')
        pkg_dict['resources'][-1]['preview'] = file_path + '.jpg'

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
