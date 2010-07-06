# -*- coding: utf-8 -*-

#  Copyright 2010 Adam Zapletal
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import re
import unittest

from generator import Generator
from parser import Parser


SAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'samples')
if (not os.path.exists(SAMPLES_DIR)):
    raise IOError('Sample source files not found, cannot run tests')


class WarningMessage(Exception):
    pass


class ErrorMessage(Exception):
    pass


class GeneratorTest(unittest.TestCase):
    def logtest(self, message, type):
        if type == 'warning':
            raise WarningMessage(message)
        elif type == 'error':
            raise ErrorMessage(message)

    def test___init__(self):
        self.assertRaises(IOError, Generator, None)
        self.assertRaises(IOError, Generator, 'foo.md')

    def test_get_toc(self):
        base_dir = os.path.join(SAMPLES_DIR, 'example1', 'slides.md')
        g = Generator(base_dir, logger=self.logtest)
        g.add_toc_entry('Section 1', 1, 1)
        g.add_toc_entry('Section 1.1', 2, 2)
        g.add_toc_entry('Section 1.2', 2, 3)
        g.add_toc_entry('Section 2', 1, 4)
        g.add_toc_entry('Section 2.1', 2, 5)
        g.add_toc_entry('Section 3', 1, 6)
        toc = g.toc
        self.assertEqual(len(toc), 3)
        self.assertEqual(toc[0]['title'], 'Section 1')
        self.assertEqual(len(toc[0]['sub']), 2)
        self.assertEqual(toc[0]['sub'][1]['title'], 'Section 1.2')
        self.assertEqual(toc[1]['title'], 'Section 2')
        self.assertEqual(len(toc[1]['sub']), 1)
        self.assertEqual(toc[2]['title'], 'Section 3')
        self.assertEqual(len(toc[2]['sub']), 0)

    def test_embed_images(self):
        base_dir = os.path.join(SAMPLES_DIR, 'example1', 'slides.md')
        g = Generator(base_dir, logger=self.logtest)
        self.assertRaises(WarningMessage, g.embed_images,
                          '<img src="toto.jpg"/>', '.')
        content = g.embed_images('<img src="monkey.jpg"/>', base_dir)
        self.assertTrue(re.match('<img src="data:image/jpeg;base64,(.+?)"/>',
                        content))

    def test_get_slide_vars(self):
        g = Generator(os.path.join(SAMPLES_DIR, 'example1', 'slides.md'))
        vars = g.get_slide_vars("<h1>heading</h1>\n<p>foo</p>\n<p>bar</p>\n", 1)
        self.assertEqual(vars['header'], '<h1>heading</h1>')
        self.assertEqual(vars['content'], '<p>foo</p>\n<p>bar</p>')
        self.assertEqual(vars['number'], 1)

    def test_get_template_vars(self):
        g = Generator(os.path.join(SAMPLES_DIR, 'example1', 'slides.md'))
        vars = g.get_template_vars(["<h1>slide1</h1>\n<p>content1</p>",
                                    "<h1>slide2</h1>\n<p>content2</p>",
                                    "<p>no heading here</p>"])
        self.assertEqual(vars['head_title'], 'slide1')
        slides = vars['slides']
        self.assertEqual(slides[0]['header'], '<h1>slide1</h1>')
        self.assertEqual(slides[0]['content'], '<p>content1</p>')
        self.assertEqual(slides[1]['header'], '<h1>slide2</h1>')
        self.assertEqual(slides[1]['content'], '<p>content2</p>')
        self.assertEqual(slides[2]['header'], None)
        self.assertEqual(slides[2]['content'], '<p>no heading here</p>')

    def test_highlight_code(self):
        g = Generator(os.path.join(SAMPLES_DIR, 'example1', 'slides.md'))
        hl = g.highlight_code("<pre><code>!php\n$foo;</code></pre>")
        self.assertTrue(hl.startswith('<pre><div class="highlight">'))
        input = "<p>Nothing to declare</p>"
        self.assertEqual(g.highlight_code(input), input)

class ParserTest(unittest.TestCase):
    def test___init__(self):
        self.assertEqual(Parser('.md').format, 'markdown')
        self.assertEqual(Parser('.markdown').format, 'markdown')
        self.assertEqual(Parser('.rst').format, 'restructuredtext')
        self.assertRaises(NotImplementedError, Parser, '.txt')

if __name__ == '__main__':
    unittest.main()
