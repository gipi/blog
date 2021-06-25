# -*- coding: utf-8 -*-

# Copyright © 2021 Gianluca Pacchiella

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from nikola.plugin_categories import ShortcodePlugin
from nikola.utils import req_missing, makedirs
try:
    import wavedrom
except ImportError:
    wavedrom = None

from hashlib import md5
import os


class WavedromShortcode(ShortcodePlugin):
    name = 'wavedrom'

    @property
    def out_dir(self):
        return os.path.join(self.site.config['OUTPUT_FOLDER'], 'wavedrom')

    def handler(self, **_options):
        if wavedrom is None:
            msg = req_missing(['wavedrom'], 'install the wavedrom package (see at https://pypi.org/project/wavedrom/).', optional=True)
            return [nodes.raw('', '<div class="text-error">{0}</div>'.format(msg), format='html')]

        diagram = _options.pop('data')
        plot_path = md5(diagram.encode()).hexdigest()

        out_path = os.path.join(self.out_dir, plot_path + '.svg')
        diagram_url = '/' + os.path.join('wavedrom', plot_path + '.svg').replace(os.sep, '/')

        svg = wavedrom.render(diagram)
        makedirs(os.path.dirname(out_path))
        svg.saveas(out_path)

        self.logger.debug("generated wavedrom at %s" % diagram_url)

        return "<img src={}/>".format(diagram_url)
