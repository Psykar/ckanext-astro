import os
import glob
import mimetypes
import paste.fileapp
import ckan.model as model
from ckan.lib.base import BaseController, c
import ckan.lib.uploader as uploader
import ckan.plugins.toolkit as toolkit

class FitsPreview(BaseController):
    def fitspreview(self, id, resource_id):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}

        try:
            rsc = toolkit.get_action('resource_show')(context, {'id': resource_id})
            toolkit.get_action('package_show')(context, {'id': id})
        except toolkit.ObjectNotFound:
            toolkit.abort(404, toolkit._('Resource not found'))
        except toolkit.NotAuthorized:
            toolkit.abort(401, toolkit._('Unauthorized to read resource %s') % id)

        if rsc.get('url_type') == 'upload':
            upload = uploader.ResourceUpload(rsc)
            filepath = upload.get_path(rsc['id'])

            jpg_glob = os.path.join(os.path.dirname(filepath), '*.jpg')
            for jpg_file in glob.glob(jpg_glob):
                if jpg_file:
                    break
            else:
                toolkit.abort(404, toolkit._('Preview not found'))

            fileapp = paste.fileapp.FileApp(jpg_file)
            try:
               status, headers, app_iter = toolkit.request.call_application(fileapp)
            except OSError:
               toolkit.abort(404, toolkit._('Resource data not found'))
            toolkit.response.headers.update(dict(headers))
            content_type, content_enc = mimetypes.guess_type(rsc.get('url',''))
            toolkit.response.headers['Content-Type'] = content_type
            toolkit.response.status = status
            return app_iter
        elif not 'url' in rsc:
            toolkit.abort(404, toolkit._('No download is available'))
        toolkit.redirect_to(rsc['url'])
